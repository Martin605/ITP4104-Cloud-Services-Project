from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_cloudformation as cloudformation,
    aws_s3 as s3,
    core
    )
from cdk.vpc_stack import VpcStack

class CdkStack(core.Stack):

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
        
        '''
        # S3 Bucket
        aws_account_id = core.Aws.ACCOUNT_ID
        
        source_bucket = "sourcebucketname%s" % (aws_account_id)
        
        s3_bucket = s3.Bucket(
            self, "SourceBucket",
            bucket_name = source_bucket
            removal_policy = core.RemovalPolicy.DESTROY
        )
        
        # VPCStack
        vpc_stack = cloudformation.CfnStack(self, "VPCStack",
            template_url = 'https://%s.s3.amazonaws.com/vpc.yaml' % (source_bucket),
            timeout_in_minutes = 5
        )'''
        
        VpcStack(self, "VpcStack")