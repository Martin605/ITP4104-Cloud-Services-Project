from aws_cdk import (
    aws_iam as iam,
    aws_cloudformation as cfn,
    aws_cognito as cognito,
    aws_lambda as lambda_,
    core
)


class CognitoStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Parameters
        parameters = core.CfnParameter(
            self, "SourceBucket",
            description="Building on AWS Cognito Stack Modified https://github.com/rosberglinhares/CloudFormationCognitoCustomResources",
            default="default"
        )

        LogoutURL = core.CfnParameter(
            self, "LogoutURL",
            type="String",
            default="http://localhost"
        )

        CallbackURL = core.CfnParameter(
            self, "CallbackURL",
            type="String",
            default="http://localhost/callback"
        )

        AppDomain = core.CfnParameter(
            self, "AppDomain",
            type="String",
            default="default"
        )
        # CognitoSNSPolicy

        CognitoSNSPolicy = iam.ManagedPolicy(
            self, 'CognitoSNSPolicy',
            description='Managed policy to allow Amazon Cognito to access SNS',
            statements=[iam.PolicyStatement(
                actions=["sns:publish"],
                resources=['*']
            )])

        # SNSRole
        sns_role = iam.CfnRole(
            self, "SNSRole",
            role_name="SNSRole",
            managed_policy_arns=CognitoSNSPolicy.att_arn,
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": [
                                "cognito-idp.amazonaws.com"
                            ]
                        },
                        "Action": [
                            "sts:AssumeRole"
                        ]
                    }
                ]
            }
        )

        # CognitoUserPool
        CognitoUserPool = cognito.CfnUserPool(
            self, 'UserPool',
            user_pool_name='photos-pool',
            alias_attributes=[
                "email", "phone_number"],
            auto_verified_attributes=[
                "email"],
            email_verification_message="Hi, Your verification code is <br/>{####}\n",
            email_verification_subject="EDX Email Verification",
            mfa_configuration="OPTIONAL",
            policies={
                "passwordPolicy": {
                    "minimumLength": 8,
                    "requireLowercase": True,
                    "requireNumbers": True,
                    "requireSymbols": True,
                    "requireUppercase": True
                }
            },
            schema=[{
                "attributeDataType": "String",
                "mutable": False,
                "name": "nickname",
                "required": True
            },
                {
                "attributeDataType": "String",
                "mutable": False,
                "name": "email",
                "required": True
            },
                {
                "attributeDataType": "String",
                "mutable": False,
                "name": "phone_number",
                "required": True
            }],
            sms_configuration={
                "externalId": "%s-external" % (core.Aws.STACK_NAME),
                "snsCallerArn": sns_role.role_arn
            }
        )
 
        # CognitoUserPoolClient
        CognitoUserPoolClient = cognito.CfnUserPoolClient(
            self, "UserPoolClient",
            client_name="WebsiteClient",
            generate_secret=True,
            user_pool_id=CognitoUserPool.ref
        )

        # CognitoCustomResourceRole
        CustomResourceRole = iam.CfnRole(
            self, "CustomResourceRole",
            role_name="cognito-resource-role",
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": [
                                "lambda.amazonaws.com"
                            ]
                        },
                        "Action": [
                            "sts:AssumeRole"
                        ]
                    }
                ]
            },
            policies=[
                {
                    "policyName": "writeCloudWatchLogs",
                    "policyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": "logs:CreateLogGroup",
                                "Resource": "arn:aws:logs:*:*:*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": "logs:CreateLogStream",
                                "Resource": "arn:aws:logs:*:*:*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": "logs:PutLogEvents",
                                "Resource": "arn:aws:logs:*:*:*"
                            }
                        ]
                    }
                },
                {
                    "policyName": "updateUserPoolClient",
                    "policyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": "cognito-idp:UpdateUserPoolClient",
                                "Resource": "arn:aws:cognito-idp:*:*:userpool/*"
                            }
                        ]
                    }
                },
                {
                    "policyName": "manageUserPoolDomain",
                    "policyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": "cognito-idp:CreateUserPoolDomain",
                                "Resource": "arn:aws:cognito-idp:*:*:userpool/*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": "cognito-idp:DeleteUserPoolDomain",
                                "Resource": "arn:aws:cognito-idp:*:*:userpool/*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": "cognito-idp:DescribeUserPoolDomain",
                                "Resource": "*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": "cognito-idp:DescribeUserPoolClient",
                                "Resource": "*"
                            }
                        ]
                    }
                },
                {
                    "policyName": "invokeLambdaFunction",
                    "policyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": "lambda:InvokeFunction",
                                "Resource": "arn:aws:lambda:*:*:function:*"
                            }
                        ]
                    }
                },
            ]
        )

        # CognitoUserPoolClientClientSettings
        with open("cdk\CognitoUserPoolClientClientSettings\index.js", encoding="utf-8") as fp:
            code_body = fp.read()

        CognitoUserPoolClientClientSettings = cfn.CustomResource(
            self, "CognitoUserPoolClientClientSettings",
            provider=cfn.CustomResourceProvider.lambda_(
                lambda_.SingletonFunction(
                    self, "CognitoUserPoolClientClientSettingsLambda",
                    uuid="f7d4f730-4ee1-11e8-9c2d-fa7ae01bbebc",
                    code=lambda_.InlineCode(code_body),
                    handler="index.handler",
                    runtime=lambda_.Runtime.NODEJS_8_10,
                    role=iam.Role.from_role_arn(
                        self, 'CustomResourceRoleiam', role_arn=CustomResourceRole.attr_arn)
                )
            ),
            properties={"UserPoolId": CognitoUserPool.ref,
                        "UserPoolClientId": CognitoUserPoolClient.ref,
                        "AppDomain": AppDomain.value_as_string,
                        "SupportedIdentityProviders": ['COGNITO'],
                        "CallbackURL": CallbackURL.value_as_string,
                        "LogoutURL": LogoutURL.value_as_string,
                        "AllowedOAuthFlowsUserPoolClient": True,
                        "AllowedOAuthFlows": ['code'],
                        "AllowedOAuthScopes": ['openid']
                        },
        )

        # CognitoIdPool
        CognitoIdPool = cognito.CfnIdentityPool(
            self, 'CognitoIdPool',
            identity_pool_name='edxcognitoidpool',
            cognito_identity_providers=[{
                "clientId": CognitoUserPoolClient.ref,
                "providerName": CognitoUserPool.attr_provider_name
            }],
            allow_unauthenticated_identities=False
        )
