from aws_cdk import (
    aws_cloudformation as cloudformation,
    aws_s3 as s3,
    core
    )

class CdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Set Parameters
        SourceBucket = core.CfnParameter(self, "SourceBucket",
            description = "Source Bucket with nested cloudformation template.",
            default = "SourceBucket"
        ) 
        
        password = core.CfnParameter(self, "Password",
            no_echo = True,
            description = "New account password",
            min_length = 1,
            max_length = 41,
            constraint_description = "the password must be between 1 and 41 characters",
            default = "Password"
        ) 
        
        db_password_parameters = core.CfnParameter(self, "DBPassword",
            no_echo = True,
            description = "New account and RDS password",
            min_length = 1,
            max_length = 41,
            constraint_description = "the password must be between 1 and 41 characters",
            default = "DBPassword"
        )
        
        AppDomain = core.CfnParameter(
            self, "AppDomain",
            description = "Unique subdomain for cognito app.",
            allowed_pattern = "^[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?$",
            constraint_description="Domain names can only contain lower-case letters, numbers, and hyphens.",
            default = "appdomain"
        )
        
        # S3 Bucket
        source_bucket = "sourcebucketname%s" % (core.Aws.ACCOUNT_ID)
        
        # s3_bucket = s3.Bucket(
        #     self, "SourceBucket",
        #     bucket_name = source_bucket,
        #     removal_policy = core.RemovalPolicy.DESTROY
        # )
        
        # VPCStack
        vpc_stack = cloudformation.CfnStack(self, "VPCStack",
            template_url = 'https://%s.s3.amazonaws.com/VpcStack.template.json' % (source_bucket),
            timeout_in_minutes = 5
        )
        
        # IAMStack
        iam_stack = cloudformation.CfnStack(self, "IAMStack",
            template_url = 'https://%s.s3.amazonaws.com/IAMStack.template.json' % (source_bucket),
            timeout_in_minutes = 5
        )

        # Cloud9Stack
        # cloud9_stack = cloudformation.CfnStack(self, "Cloud9Stack",
        #     template_url = 'https://%s.s3.amazonaws.com/Cloud9Stack.template.json' % (source_bucket),
        #     timeout_in_minutes = 5,
        #     parameters = {
        #         "PublicSubnet1" : core.Fn.import_value("PublicSubnet1")
        #     }
        # )
        
        # SecurityStack
        # security_stack = cloudformation.CfnStack(self, "SecurityStack",
        #     template_url = 'https://%s.s3.amazonaws.com/SecurityStack.template.json' % (source_bucket),
        #     timeout_in_minutes = 5,
        #     parameters = {
        #         "EC2VpcId" : core.Fn.import_value("VPC"),
        #         "EdxProjectCloud9Sg" : core.Fn.import_value("EdxProjectCloud9Sg")
        #     }
        # )