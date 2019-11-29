from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_cloudformation as cloudformation,
    aws_s3 as s3,
    aws_cloud9 as cloud9,
    aws_rds as rds,
    core
    )


class DBStack(core.Construct):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Exercise 7
        # Set Parameters
        ec2_vpc_id_parameters = core.CfnParameter(self, "EC2VpcId",
            description = "AWS::EC2::VPC::Id",
            default = "default"
        )
        
        private_subnet_1_parameters = core.CfnParameter(self, "PrivateSubnet1",
            description = "AWS::EC2::Subnet::Id",
            default = "default"
        )
        
        private_subnet_2_parameters = core.CfnParameter(self, "PrivateSubnet2",
            description = "AWS::EC2::Subnet::Id",
            default = "default"
        )
        
        password_parameters = core.CfnParameter(self, "DBPassword",
            no_echo = True,
            description = "New account and RDS password",
            min_length = 1,
            max_length = 41,
            constraint_description = "the password must be between 1 and 41 characters",
            default = "default"
        )

        # DBSecurityGroup:
        db_security_group = rds.CfnDBSecurityGroup(self, "DBSecurityGroup",
            ec2_vpc_id = core.Fn.import_value("VPC"),
            db_security_group_ingress = { 
                "CIDRIP" : "10.1.0.0/16"
            },
            group_description = "Frontend Access"
        )