from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_cloudformation as cloudformation,
    aws_s3 as s3,
    aws_cloud9 as cloud9,
    core
    )
from cdk.vpc_stack import VpcStack
from cdk.iam_stack import IAMStack
from cdk.cloud9_stack import Cloud9Stack
from cdk.web_stack import WebStack
class CdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
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
        )
        # IAMStack
        iam_stack = cloudformation.CfnStack(self, "IAMStack",
            template_url = 'https://%s.s3.amazonaws.com/iam.yaml' % (source_bucket),
            timeout_in_minutes = 5,
            parameters = password_parameters
        # Cloud9Stack
        cloud9_stack = cloudformation.CfnStack(self, "Cloud9Stack",
            template_url = 'https://%s.s3.amazonaws.com/cloud9.yaml' % (source_bucket),
            timeout_in_minutes = 5,
            parameters = {
                "PublicSubnet1" : core.Fn.import_value("PublicSubnet1")
            }
        '''
        
        cloud9_stack = Cloud9Stack(self, "Cloud9Stack")
        iam_stack = IAMStack(self, "IAMStack")
        vpc_stack = VpcStack(self, "VpcStack")
        web_stack = WebStack(self, "WebStack",
                ec2_vpc_id = 'vpc_stack.vpc',
                private_subnet_1="vpc_stack.private_subnet_1",
                private_subnet_2="vpc_stack.private_subnet_2",
                web_server_instance_profile="security_stack.web_server_instance_profile",
                web_server_role="security_stack.web_server_role",
                web_security_group="security_stack.web_security_group",
                load_balancer_arn="cdn_stack.load_balancer_arn"
                )
        # web_stack = WebStack(self, "WebStack", 
        #         ec2_vpc_id = vpc_stack.vpc,
        #         private_subnet_1=vpc_stack.private_subnet_1,
        #         private_subnet_2=vpc_stack.private_subnet_2,
        #         web_server_instance_profile=security_stack.web_server_instance_profile,
        #         web_server_role=security_stack.web_server_role,
        #         web_security_group=security_stack.web_security_group,
        #         load_balancer_arn=cdn_stack.load_balancer_arn
        #         )
    