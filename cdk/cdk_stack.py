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
from cdk.db_stack import DBStack
class CdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        Cloud9Stack(self, "Cloud9Stack")
        IAMStack(self, "IAMStack")
        VpcStack(self, "VpcStack")
        