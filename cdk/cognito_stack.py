from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_cloudformation as cloudformation,
    aws_s3 as s3,
    aws_cloud9 as cloud9,
    aws_cognito as cognito,
    aws_lambda as lambda_,
    core
    )

class CognitoStack(core.Construct):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # Description
        parameters = core.CfnParameter(self, "SourceBucket",
            description = "Building on AWS Cognito Stack Modified https://github.com/rosberglinhares/CloudFormationCognitoCustomResources",
            default = "default"
        )
        # Parameters
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
                "PasswordPolicy" : {
                    "MinimumLength" : 8,
                    "RequireLowercase" : True,
                    "RequireNumbers" : True,
                    "RequireSymbols" : True,
                    "RequireUppercase" : True
                }
            },
            schema =[{
                "AttributeDataType" : "string",
                "Mutable" : False,
                "Name" : "nickname",
                "Required" : True
            },
                {"AttributeDataType" : "string",
                "Mutable" : False,
                "Name" : "email",
                "Required" : True
            },
                {"AttributeDataType" : "string",
                "Mutable" : False,
                "Name" : "phone_number",
                "Required" : True
            }],
            sms_configuration = {
                "ExternalId" : "%s-external" % (core.Aws.STACK_NAME),
                "SnsCallerArn" : sns_role.role_id
            }
        )
        # CognitoUserPoolClient
        UserPoolClient = cognito.CfnUserPoolClient(self,"UserPoolClient",
            client_name  = "WebsiteClient",
            generate_secret = True,
            user_pool_id = cognito_user_pool.ref
        )
        # CognitoCustomResourceRole
        # CustomResourceRole = iam.CfnRole(self,"CustomResourceRole",
        #     role_name = "cognito_resource_role",
        #     assume_role_policy_document=
        #         {
        #             "Version": "2012-10-17",
        #             "Statement": [
        #                 {
        #                     "Effect": "Allow",
        #                     "Principal": {
        #                         "Service": [
        #                             "lambda.amazonaws.com"
        #                         ]
        #                     },
        #                     "Action": [
        #                         "sts:AssumeRole"
        #                     ]
        #                 }
        #             ]
        #         },
        #     policies = [
        #         {
        #             "policyName" : "WriteCloudWatchLogs",
        #             "policyDocument" : {
        #                 "Version":"2012-10-17",
        #                 "Statement":[
        #                     {
        #                         "Effect": "Allow",
        #                         "Action": "logs:CreateLogGroup",
        #                         "Resource" :"arn:aws:logs:*:*:*"
        #                     },
        #                     {
        #                         "Effect": "Allow",
        #                         "Action": "logs:CreateLogStream",
        #                         "Resource" :"arn:aws:logs:*:*:*"
        #                     },
        #                     {
        #                         "Effect": "Allow",
        #                         "Action": "logs:PutLogEvents",
        #                         "Resource" :"arn:aws:logs:*:*:*"
        #                     }
        #                 ]
        #             }
        #         },
        #         {
        #             "policyName" : "UpdateUserPoolClient",
        #             "policyDocument" : {
        #                 "Version":"2012-10-17",
        #                 "Statement":[
        #                     {
        #                         "Effect": "Allow",
        #                         "Action": "cognito-idp:UpdateUserPoolClient",
        #                         "Resource" :"arn:aws:cognito-idp:*:*:userpool/*"
        #                     }
        #                 ]
        #             }
        #         },
        #         {
        #             "policyName" : "ManageUserPoolDomain",
        #             "policyDocument" : {
        #                 "Version":"2012-10-17",
        #                 "Statement":[
        #                     {
        #                         "Effect": "Allow",
        #                         "Action": "cognito-idp:CreateUserPoolDomain",
        #                         "Resource" :"arn:aws:cognito-idp:*:*:userpool/*"
        #                     },
        #                     {
        #                         "Effect": "Allow",
        #                         "Action": "cognito-idp:DeleteUserPoolDomain",
        #                         "Resource" :"arn:aws:cognito-idp:*:*:userpool/*"
        #                     },
        #                     {
        #                         "Effect": "Allow",
        #                         "Action": "cognito-idp:DescribeUserPoolDomain",
        #                         "Resource" :"*"
        #                     },
        #                     {
        #                         "Effect": "Allow",
        #                         "Action": "cognito-idp:DescribeUserPoolClient",
        #                         "Resource" :"*"
        #                     }
        #                 ]
        #             }
        #         },
        #         {
        #             "policyName" : "InvokeLambdaFunction",
        #             "policyDocument" : {
        #                 "Version":"2012-10-17",
        #                 "Statement":[
        #                     {
        #                         "Effect": "Allow",
        #                         "Action": "lambda:InvokeFunction",
        #                         "Resource" :"arn:aws:lambda:*:*:function:*"
        #                     }
        #                 ]
        #             }
        #         },
        #     ]
        # )
        # # # WriteCloudWatchLogs
        # # WriteCloudWatchLogs = iam.CfnPolicy(self, "WriteCloudWatchLogs",
        # #     policy_name = "WriteCloudWatchLogs",
        # #     policy_document = {
        # #         "Version" : "2012-10-17",
        # #         "Statement" :[
        # #             {
        # #                 "Effect": "Allow",
        # #                 "Action": "logs:CreateLogGroup",
        # #                 "Resource" :"arn:aws:logs:*:*:*"
        # #             },
        # #             {
        # #                 "Effect": "Allow",
        # #                 "Action": "logs:CreateLogStream",
        # #                 "Resource" :"arn:aws:logs:*:*:*"
        # #             },
        # #             {
        # #                 "Effect": "Allow",
        # #                 "Action": "logs:PutLogEvents",
        # #                 "Resource" :"arn:aws:logs:*:*:*"
        # #             }
        # #         ]
        # #     },
        # #   roles = [CustomResourceRole.role_arn]
        # #  )
        # # # UpdateUserPoolClient
        # # UpdateUserPoolClient = iam.CfnPolicy(self, "UpdateUserPoolClient",
        # #     policy_name = "UpdateUserPoolClient",
        # #     policy_document = {
        # #         "Version" : "2012-10-17",
        # #         "Statement" :[
        # #             {
        # #                 "Effect": "Allow",
        # #                 "Action": "cognito-idp:UpdateUserPoolClient",
        # #                 "Resource" :"arn:aws:cognito-idp:*:*:userpool/*"
        # #             }
        # #         ]
        # #     },
        # #   roles = [CustomResourceRole.role_arn]
        # #  )
        # # # ManageUserPoolDomain
        # # ManageUserPoolDomain = iam.CfnPolicy(self, "ManageUserPoolDomain",
        # #     policy_name = "ManageUserPoolDomain",
        # #     policy_document = {
        # #         "Version" : "2012-10-17",
        # #         "Statement" :[
        # #             {
        # #                 "Effect": "Allow",
        # #                 "Action": "cognito-idp:CreateUserPoolDomain",
        # #                 "Resource" :"arn:aws:cognito-idp:*:*:userpool/*"
        # #             },
        # #             {
        # #                 "Effect": "Allow",
        # #                 "Action": "cognito-idp:DeleteUserPoolDomain",
        # #                 "Resource" :"arn:aws:cognito-idp:*:*:userpool/*"
        # #             },
        # #             {
        # #                 "Effect": "Allow",
        # #                 "Action": "cognito-idp:DescribeUserPoolDomain",
        # #                 "Resource" :"*"
        # #             },
        # #             {
        # #                 "Effect": "Allow",
        # #                 "Action": "cognito-idp:DescribeUserPoolClient",
        # #                 "Resource" :"*"
        # #             }
        # #         ]
        # #     },
        # #   roles = [CustomResourceRole.role_arn]
        # #  )
        # # # InvokeLambdaFunction
        # # InvokeLambdaFunction = iam.CfnPolicy(self, "InvokeLambdaFunction",
        # #     policy_name = "InvokeLambdaFunction",
        # #     policy_document = {
        # #         "Version" : "2012-10-17",
        # #         "Statement" :[
        # #             {
        # #                 "Effect" : "Allow",
        # #                 "Action": "lambda:InvokeFunction",
        # #                 "Resource" :"arn:aws:lambda:*:*:function:*"
        # #             }
        # #         ]
        # #     },
        # #   roles = [CustomResourceRole.role_arn]
        # #  )
        # # CognitoUserPoolClientClientSettings
        # ClientSettingsFunction = lambda_.CfnFunction(self,"ClientSettingsFunction",
        #     function_name = "CloudFormationCognitoUserPoolClientSettings",
        #     runtime = "nodejs8.10",
        #     handler = "lambda.handler",
        #     code = lambda_.Code.asset("./cdk/lambda"),
        #     role = CustomResourceRole.role_arn
        # )


        # ClientSettings = cognito.CfnUserPoolClient(self,"UserPoolClient",
            
        # )