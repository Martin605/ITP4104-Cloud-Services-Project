from aws_cdk import (
    aws_iam as iam,
    aws_cloud9 as cloud9,
    aws_lambda as lambda_,
    aws_ec2 as ec2,
    core
    )
    
class Cloud9Stack(core.Construct):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Exercise 5
        # Set Parameters
        
        
        # LambdaExecutionRole
        lambda_execution_role = iam.CfnRole(self, "LambdaExecutionRole",
            role_name= "lambda-execution-role",
            assume_role_policy_document = {
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
                }]
            },
            path = "/",
            policies = [
            {
                "policyName" : "root",
                "policyDocument" : {
                    "Version":"2012-10-17",
                    "Statement" : [
                    {
                        "Effect": "Allow",
                        "Action" : [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents"
                        ],
                        "Resource": "arn:aws:logs:*:*:*"
                    },
                    {
                        "Effect" : "Allow",
                        "Action" : [
                            "ec2:Describe*"
                         ],
                        "Resource": "*"
                    }]
                }
            }]
        )
        
        # EdxProjectCloud9
        edx_project_cloud9 = cloud9.CfnEnvironmentEC2(self, "EdxProjectCloud9",
            automatic_stop_time_minutes = 30,
            instance_type = "t2.micro",
            name = "BuildingOnAWS%s" % (core.Aws.STACK_NAME),
            subnet_id = core.Fn.import_value("PublicSubnet1")
        )
        edx_project_cloud9.apply_removal_policy(core.RemovalPolicy.DESTROY)
        
        # CustomFunction
        custom_function = lambda_.Function(self,"CustomFunction",
            runtime = lambda_.Runtime.NODEJS_8_10,
            handler = "custom_function.handler",
            code = lambda_.Code.asset('./cdk/lambda'),
            timeout = core.Duration.seconds(30),
            role = iam.Role.from_role_arn(self, 'role_id', lambda_execution_role.attr_arn)
        )
        
        # CustomResource
        # custom_resourcce = core.CfnResource(self, "CustomResource",
        #     type = "Custom::CustomResource",
        #     properties = {
        #         "ServiceToken" : custom_function.function_arn,
        #         "EdxProjectCloud9" : edx_project_cloud9.ref
        #     }
        # )
        
        
        # Output
        core.CfnOutput(self, "EdxProjectCloud9Output",
          value = edx_project_cloud9.ref,
          description = "Edx User Cloud9",
          export_name = "EdxProjectCloud9"
        )
        
        # core.CfnOutput(self, "EdxProjectCloud9SgOutput",
        #   value = custom_resourcce.ref,
        #   description = "Edx User Cloud9 Security Group ID",
        #   export_name = "EdxProjectCloud9Sg"
        # )