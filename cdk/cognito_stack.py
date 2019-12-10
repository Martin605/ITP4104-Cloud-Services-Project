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
        parameters = core.CfnParameter(self, "SourceBucket",
                                       description="Building on AWS Cognito Stack Modified https://github.com/rosberglinhares/CloudFormationCognitoCustomResources",
                                       default="default"
                                       )

        LogoutURL = core.CfnParameter(self, "LogoutURL",
                                      type="String",
                                      default="http://localhost"
                                      )

        CallbackURL = core.CfnParameter(self, "CallbackURL",
                                        type="String",
                                        default="http://localhost/callback"
                                        )

        AppDomain = core.CfnParameter(self, "AppDomain",
                                      type="String",
                                      default="default"
                                      )

        # SNSRole
        sns_role = iam.Role(
            self, "SNSRole",
            role_name="SNSRole",
            assumed_by=iam.ServicePrincipal('cognito-idp.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    'AmazonSNSFullAccess')
            ]
        )

        # CognitoUserPool
        CognitoUserPool = cognito.CfnUserPool(self, 'UserPool',
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
        CognitoUserPoolClient = cognito.CfnUserPoolClient(self, "UserPoolClient",
                                                          client_name="WebsiteClient",
                                                          generate_secret=True,
                                                          user_pool_id=CognitoUserPool.ref
                                                          )

        # CognitoCustomResourceRole
        CustomResourceRole = iam.CfnRole(self, "CustomResourceRole",
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

        CloudFormationCognitoUserPoolClientSettings = lambda_.CfnFunction(self,"CloudFormationCognitoUserPoolClientSettings",
            runtime = "nodejs8.10",
            handler = "index.handler",
            code = {"zipFile":
            "const AWS = require('aws-sdk');\n"
            "const response = require('cfn-response');\n"
            "const cognitoIdentityServiceProvider = new AWS.CognitoIdentityServiceProvider();\n"
            "exports.handler = (event, context) => {\n"
            "      try {\n"
            "            switch (event.RequestType) {\n"
            "                  case 'Create':\n"
            "                  case 'Update':\n"
            "                        cognitoIdentityServiceProvider.updateUserPoolClient({\n"
            "                              UserPoolId: event.ResourceProperties.UserPoolId,\n"
            "                              ClientId: event.ResourceProperties.UserPoolClientId,\n"
            "                              SupportedIdentityProviders: event.ResourceProperties.SupportedIdentityProviders,\n"
            "                              CallbackURLs: [event.ResourceProperties.CallbackURL],\n"
            "                              LogoutURLs: [event.ResourceProperties.LogoutURL],\n"
            "                              AllowedOAuthFlowsUserPoolClient: (event.ResourceProperties.AllowedOAuthFlowsUserPoolClient == 'true'),\n"
            "                              AllowedOAuthFlows: event.ResourceProperties.AllowedOAuthFlows,\n"
            "                              AllowedOAuthScopes: event.ResourceProperties.AllowedOAuthScopes\n"
            "                        })\n"
            "                              .promise()\n"
            "                              .then(data => {\n"
            "                                    let params = {\n"
            "                                          Domain: event.ResourceProperties.AppDomain,\n"
            "                                          UserPoolId: event.ResourceProperties.UserPoolId\n"
            "                                    };\n"
            "                                    console.log(params);\n"
            "                                    return cognitoIdentityServiceProvider.createUserPoolDomain(params).promise();\n"
            "                              })\n"
            "                              .then(data => {\n"
            "                                    let params = {\n"
            "                                          ClientId: event.ResourceProperties.UserPoolClientId,\n"
            "                                          UserPoolId: event.ResourceProperties.UserPoolId\n"
            "                                    };\n"
            "                                    return cognitoIdentityServiceProvider.describeUserPoolClient(params).promise();\n"
            "                              })\n"
            "                              .then(data => {\n"
            "                                    console.log(data);\n"
            "                                    let responseData = { ClientSecret: data.UserPoolClient.ClientSecret };\n"
            "                                    console.log(responseData);\n"
            "                                    response.send(event, context, response.SUCCESS, responseData);\n"
            "                              })\n"
            "                              .catch(err => {\n"
            "                                    console.error(err);\n"
            "                                    response.send(event, context, response.FAILED, {});\n"
            "                              });\n"
            "\n"
            "                        break;\n"
            "\n"
            "                  case 'Delete':\n"
            "                        let params = {\n"
            "                              Domain: event.ResourceProperties.AppDomain,\n"
            "                              UserPoolId: event.ResourceProperties.UserPoolId\n"
            "                        };\n"
            "                        cognitoIdentityServiceProvider.deleteUserPoolDomain(params).promise()\n"
            "                              .then(data => response.send(event, context, response.SUCCESS, {}))\n"
            "                              .catch(error => response.send(event, context, response.FAILED, {}));\n"
            "                        break;\n"
            "            }\n"
            "\n"
            "            console.info(`CognitoUserPoolClientSettings Success for request type ${event.RequestType}`);\n"
            "      } catch (error) {\n"
            "            console.error(`CognitoUserPoolClientSettings Error for request type ${event.RequestType}:`, error);\n"
            "            response.send(event, context, response.FAILED, {});\n"
            "      }\n"
            "}"
            },
            role = CustomResourceRole.attr_arn
        )

        # #CognitoUserPoolClientClientSettings
        CognitoUserPoolClientClientSettings = cfn.CfnCustomResource(self,
                                                                    "CognitoUserPoolClientClientSettings", service_token=CloudFormationCognitoUserPoolClientSettings.attr_arn)
        CognitoUserPoolClientClientSettings.add_property_override(
            "UserPoolId", CognitoUserPool.ref)
        CognitoUserPoolClientClientSettings.add_property_override(
            "UserPoolClientId", CognitoUserPoolClient.ref)
        CognitoUserPoolClientClientSettings.add_property_override(
            "AppDomain", AppDomain.value_as_string)
        CognitoUserPoolClientClientSettings.add_property_override(
            "SupportedIdentityProviders", ['COGNITO'])
        CognitoUserPoolClientClientSettings.add_property_override(
            "CallbackURL", CallbackURL.value_as_string)
        CognitoUserPoolClientClientSettings.add_property_override(
            "LogoutURL", LogoutURL.value_as_string)
        CognitoUserPoolClientClientSettings.add_property_override(
            "AllowedOAuthFlowsUserPoolClient", True)
        CognitoUserPoolClientClientSettings.add_property_override(
            "AllowedOAuthFlows", ['code']),
        CognitoUserPoolClientClientSettings.add_property_override(
            "AllowedOAuthScopes", ['openid'])

        # CognitoIdPool
        CognitoIdPool = cognito.CfnIdentityPool(self,'CognitoIdPool',
        identity_pool_name='edxcognitoidpool',
        cognito_identity_providers=[{
            "clientId": CognitoUserPoolClient.ref,
            "providerName": CognitoUserPool.attr_provider_name
            }],
        allow_unauthenticated_identities=False
        )
