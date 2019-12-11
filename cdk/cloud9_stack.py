from aws_cdk import (
    aws_iam as iam,
    aws_cloud9 as cloud9,
    aws_lambda as lambda_,
    aws_cloudformation as cfn,
    aws_ec2 as ec2,
    core
    )
    
class Cloud9Stack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Exercise 9
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
        custom_function = lambda_.CfnFunction(self,"CustomFunction",
            runtime = "nodejs8.10",
            handler = "index.handler",
            code = {
"zipFile": "const response = require('cfn-response');\n"
"const AWS = require('aws-sdk');\n"
"exports.handler = (event, context) => {\n"
    "let params = {\n"
        "Filters: [\n"
        "{\n"
            "Name: 'tag:aws:cloud9:environment',\n"
            "Values: [\n"
                "event.ResourceProperties.EdxProjectCloud9\n"
            "]\n"
        "}\n"
        "]\n"
    "};\n"
    "let ec2 = new AWS.EC2();\n"
    "ec2.describeInstances(params, (err, data) => {\n"
        "if (err) {\n"
            "console.log(err, err.stack); // an error occurred\n"
            "response.send(event, context, response.FAILED, {});\n"
        "}else{\n"
            "let responseData = {Value: data.Reservations[0].Instances[0].SecurityGroups[0].GroupId};\n"       
            "console.log(responseData);\n"
            "response.send(event, context, response.SUCCESS, responseData);\n"
        "}\n"        
    "});\n"
"};"
            },
            timeout = 30,
            role = lambda_execution_role.attr_arn
        )
        
        # CustomResource
        custom_resource = cfn.CfnCustomResource( self, "CustomResource",
            service_token = custom_function.attr_arn,
        )
        custom_resource.add_override("Properties.EdxProjectCloud9", edx_project_cloud9.ref)
        
        # Output
        core.CfnOutput(self, "EdxProjectCloud9Output",
            value = edx_project_cloud9.ref,
            description = "Edx User Cloud9",
            export_name = "EdxProjectCloud9"
        )
        
        core.CfnOutput(self, "EdxProjectCloud9SgOutput",
            value = core.Fn.get_att(custom_resource.logical_id, "Value").to_string(),
            description = "Edx User Cloud9 Security Group ID",
            export_name = "EdxProjectCloud9Sg"
        )
