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

class Cloud9Stack(core.Construct):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        vpc_stack = VpcStack(self, "VpcStack")
        iam_stack = IAMStack(self, "IAMStack")
        
        # Exercise 5
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
        
        # EdxProjectCloud9
        edx_project_cloud9 = cloud9.CfnEnvironmentEC2(self, "EdxProjectCloud9",
            owner_arn = iam_stack.edXProjectUser,
            description = "Building On AWS Cloud9",
            automatic_stop_time_minutes = 30,
            instance_type = "t2.micro",
            name = "BuildingOnAWS",
            subnet_id = vpc_stack.PublicSubnet1
        )
        edx_project_cloud9.apply_removal_policy(core.RemovalPolicy.DESTROY)
        
        # ImageS3Bucket
        image_s3_bucket = s3.Bucket(self, "ImageS3Bucket",
            bucket_name = "imagebucket%s" % (core.Aws.ACCOUNT_ID),
            removal_policy=core.RemovalPolicy.DESTROY
        )
        
        # Output
        core.CfnOutput(self, "EdxProjectCloud9Output",
            value = edx_project_cloud9.ref,
            description = "Edx User Cloud9",
            export_name = "EdxProjectCloud9"
        )
        
        self.EdxProjectCloud9Output = edx_project_cloud9.ref