from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_cloudformation as cloudformation,
    aws_s3 as s3,
    core
    )

class IAMStack(core.Construct):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Exercise 4
        # Set Parameters
        parameters = core.CfnParameter(self, "SourceBucket",
            description = "Source Bucket with nested cloudformation template",
            default = "default"
        )
        
        password_parameters = core.CfnParameter(self, "Password",
            no_echo = True,
            description = "New account password",
            min_length = 1,
            max_length = 41,
            constraint_description = "the password must be between 1 and 41 characters",
            default = "default"
        )
        
        # CFNUser
        cfn_user = iam.CfnUser(self, "CFNUser",
            user_name = "edXProjectUser",
            login_profile = {
                "password" : password_parameters.value_as_string
            }
        )   
        
        # CFNUserGroup
        cfn_user_group = iam.CfnGroup(self, "CFNUserGroup",
        )
        
        # Users
        users_to_group = iam.CfnUserToGroupAddition(self, "UserToGroupAddition",
            group_name = cfn_user_group.ref,
            users = [cfn_user.ref]
        )

        # CFNUserPolicies
        cfn_user_policies = iam.CfnPolicy(self, "CFNUserPolicies",
            policy_name = "edXProjectPolicy",
            policy_document = {
                "Version" : "2012-10-17",
                "Statement" : [{
                    "Sid" : "Sid1",
                    "Effect" : "Allow",
                    "Action" : [
                        "iam:*",
                        "rds:*",
                        "sns:*",
                        "cloudformation:*",
                        "rekognition:*",
                        "ec2:*",
                        "cognito-idp:*",
                        "sqs:*",
                        "xray:*",
                        "s3:*",
                        "elasticloadbalancing:*",
                        "cloud9:*",
                        "lambda:*",
                        "tag:GetResources",
                        "logs:*",
                        "kms:ListRetirableGrants",
                        "kms:GetKeyPolicy",
                        "kms:ListResourceTags",
                        "kms:ReEncryptFrom",
                        "kms:ListGrants",
                        "kms:GetParametersForImport",
                        "kms:ListKeys",
                        "kms:GetKeyRotationStatus",
                        "kms:ListAliases",
                        "kms:ReEncryptTo",
                        "kms:DescribeKey"
                    ],
                    "Resource": "*",
                }]
            },
            groups = [cfn_user_group.ref]
        )
        
        # CFNKeys
        cfn_keys = iam.CfnAccessKey(self, "CFNKeys",
            user_name = cfn_user.ref
        )
        
        
        
        # Output
        core.CfnOutput(self, "AccessKeyOutput",
            value = cfn_keys.ref,
            description = "AWSAccessKeyId of new user",
            export_name = "AccessKey"
        )
        core.CfnOutput(self, "SecretKeyOutput",
            value = cfn_keys.attr_secret_access_key,
            description = "AWSSecretKey of new user",
            export_name = "SecretKey"
        )
        core.CfnOutput(self, "edXProjectUser",
            value = cfn_user.attr_arn,
            description = "edXProjectUser",
            export_name = "edXProjectUser"
        )
        
        