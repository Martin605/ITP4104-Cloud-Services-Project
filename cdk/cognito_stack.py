from aws_cdk import (
    aws_iam as iam,
    aws_cloudformation as cfn,
    aws_cognito as cognito,
    aws_lambda as lambda_,
    core
    )

class CognitoStack(core.Construct):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Parameters
        parameters = core.CfnParameter(self, "SourceBucket",
            description = "Building on AWS Cognito Stack Modified https://github.com/rosberglinhares/CloudFormationCognitoCustomResources",
            default = "default"
        )
        
        
        LogoutURL = core.CfnParameter(self,"LogoutURL",
            type = "String",
            default = "http://localhost"
        )
         
        CallbackURL = core.CfnParameter(self,"CallbackURL",
            type = "String",
            default = "http://localhost/callback"
        )
        
        AppDomain = core.CfnParameter(self,"AppDomain",
            type = "String",
            default = "default"
        )
        
        # SNSRole
        sns_role = iam.Role(
            self, "SNSRole",
            role_name="SNSRole",
            assumed_by=iam.ServicePrincipal('cognito-idp.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSNSFullAccess')
            ]
        )
        
        # CognitoUserPool
        cognito_user_pool = cognito.CfnUserPool(self, 'UserPool', 
            user_pool_name = 'photos-pool',
            alias_attributes = ["email","phone_number"],
            auto_verified_attributes = ["email"],
            email_verification_message = "Hi, Your verification code is <br/>{####}\n",
            email_verification_subject = "EDX Email Verification",
            mfa_configuration ="OPTIONAL",
            policies = {
                "passwordPolicy" : {
                    "minimumLength" : 8,
                    "requireLowercase" : True,
                    "requireNumbers" : True,
                    "requireSymbols" : True,
                    "requireUppercase" : True
                }
            },
            schema =[{
                "attributeDataType" : "String",
                "mutable" : False,
                "name" : "nickname",
                "required" : True
            },
                {
                "attributeDataType" : "String",
                "mutable" : False,
                "name" : "email",
                "required" : True
            },
                {
                "attributeDataType" : "String",
                "mutable" : False,
                "name" : "phone_number",
                "required" : True
            }],
            sms_configuration = {
                "externalId" : "%s-external" % (core.Aws.STACK_NAME),
                "snsCallerArn" : sns_role.role_arn
            }
        )
        
        # CognitoUserPoolClient
        UserPoolClient = cognito.CfnUserPoolClient(self,"UserPoolClient",
            client_name  = "WebsiteClient",
            generate_secret = True,
            user_pool_id = cognito_user_pool.ref
        )
        
        #CognitoCustomResourceRole
        CustomResourceRole = iam.CfnRole(self,"CustomResourceRole",
            role_name = "cognito-resource-role",
            assume_role_policy_document=
                {
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
            policies = [
                {
                    "policyName" : "writeCloudWatchLogs",
                    "policyDocument" : {
                        "Version":"2012-10-17",
                        "Statement":[
                            {
                                "Effect": "Allow",
                                "Action": "logs:CreateLogGroup",
                                "Resource" :"arn:aws:logs:*:*:*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": "logs:CreateLogStream",
                                "Resource" :"arn:aws:logs:*:*:*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": "logs:PutLogEvents",
                                "Resource" :"arn:aws:logs:*:*:*"
                            }
                        ]
                    }
                },
                {
                    "policyName" : "updateUserPoolClient",
                    "policyDocument" : {
                        "Version":"2012-10-17",
                        "Statement":[
                            {
                                "Effect": "Allow",
                                "Action": "cognito-idp:UpdateUserPoolClient",
                                "Resource" :"arn:aws:cognito-idp:*:*:userpool/*"
                            }
                        ]
                    }
                },
                {
                    "policyName" : "manageUserPoolDomain",
                    "policyDocument" : {
                        "Version":"2012-10-17",
                        "Statement":[
                            {
                                "Effect": "Allow",
                                "Action": "cognito-idp:CreateUserPoolDomain",
                                "Resource" :"arn:aws:cognito-idp:*:*:userpool/*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": "cognito-idp:DeleteUserPoolDomain",
                                "Resource" :"arn:aws:cognito-idp:*:*:userpool/*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": "cognito-idp:DescribeUserPoolDomain",
                                "Resource" :"*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": "cognito-idp:DescribeUserPoolClient",
                                "Resource" :"*"
                            }
                        ]
                    }
                },
                {
                    "policyName" : "invokeLambdaFunction",
                    "policyDocument" : {
                        "Version":"2012-10-17",
                        "Statement":[
                            {
                                "Effect": "Allow",
                                "Action": "lambda:InvokeFunction",
                                "Resource" :"arn:aws:lambda:*:*:function:*"
                            }
                        ]
                    }
                },
            ]
        )
        
        # CloudFormationCognitoUserPoolClientSettings
        ClientSettingsFunction = lambda_.Function(self,"ClientSettingsFunction",
            runtime = lambda_.Runtime.NODEJS_8_10,
            handler = "lambda.handler",
            code = lambda_.Code.asset('./cdk/lambda'),
            role = iam.Role.from_role_arn(self, 'role_id', CustomResourceRole.attr_arn)
        )
        
        # #CognitoUserPoolClientClientSettings
        # client_settings = core.CfnResource(self, "CognitoUserPoolClientClientSettings",
        #     type = "Custom::CognitoUserPoolClientSettings",
        #     properties = {
        #         "ServiceToken" : ClientSettingsFunction.function_arn,
        #         "UserPoolId" : cognito_user_pool.ref,
        #         "UserPoolClientId" : UserPoolClient.ref,
        #         "AppDomain" : UserPoolClient.ref,
        #     }
        # )
        # )
    #       CognitoUserPoolClientClientSettings:
    # Type: Custom::CognitoUserPoolClientSettings
    # Properties:
    #   ServiceToken: !GetAtt CloudFormationCognitoUserPoolClientSettings.Arn
    #   UserPoolId: !Ref CognitoUserPool
    #   UserPoolClientId: !Ref CognitoUserPoolClient
    #   AppDomain: !Ref AppDomain
    #   SupportedIdentityProviders:
    #     - COGNITO
    #   CallbackURL:  !Ref CallbackURL
    #   LogoutURL: !Ref LogoutURL
    #   AllowedOAuthFlowsUserPoolClient: true
    #   AllowedOAuthFlows:
    #     - code
    #   AllowedOAuthScopes:
    #     - openid