from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    core
    )

class SecurityStack(core.Stack):

  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)
    
    # Exercise 11
    # WebServerRole
    web_server_role = iam.CfnRole(self, "WebServerRole",
      role_name= "ec2-webserver-role",
      assume_role_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": [
              "ec2.amazonaws.com"
            ]
          },
          "Action": [
            "sts:AssumeRole"
          ]
        }]
      },
      managed_policy_arns = [
        "arn:aws:iam::aws:policy/AmazonS3FullAccess",
        "arn:aws:iam::aws:policy/AmazonRekognitionReadOnlyAccess",
        "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM",
        "arn:aws:iam::aws:policy/AmazonPollyReadOnlyAccess",
        "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
      ],
      path = "/",
      policies = [
        {
          "policyName" : "SystemsManagerParameters",
          "policyDocument" : {
            "Version":"2012-10-17",
            "Statement" : [
            {
              "Effect": "Allow",
              "Action" : [
                "ssm:DescribeParameters"
              ],
                "Resource": "*"
            },
            {
              "Effect" : "Allow",
              "Action" : [
                "ssm:GetParameters"
              ],
              "Resource": {"Fn::Sub" : "arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/edx-*"}
            }]
          }
        },
        {
          "policyName" : "LogRolePolicy",
          "policyDocument" : {
            "Version":"2012-10-17",
            "Statement" : [
            {
              "Effect" : "Allow",
              "Action" : [
              'logs:CreateLogGroup',
              'logs:CreateLogStream',
              'logs:PutLogEvents',
              'logs:DescribeLogStreams'
            ],
              "Resource": {"Fn::Sub" : "arn:aws:logs::${AWS::Region}:*:*"}
            }]
          }
        }
      ]
    )
    
    # WebServerInstanceProfile
    web_server_instance_profile = iam.CfnInstanceProfile(self, "WebServerInstanceProfile",
      instance_profile_name = "webserverinstanceprofile",
      path = "/",
      roles = [web_server_role.role_name]
    )
    
    # WebSecurityGroup
    web_security_group = ec2.CfnSecurityGroup(self, "WebSecurityGroup",
      group_name = "web-server-sg",
      group_description =  "HTTP traffic",
      vpc_id = core.Fn.import_value("VPC"),
      security_group_ingress = [
        {
          "ipProtocol" : "tcp",
          "fromPort" : 80,
          "toPort" : 80,
          "cidrIp" : "0.0.0.0/0"
        }
      ],
      security_group_egress = [
        {
          "ipProtocol" : "tcp",
          "fromPort" : 0,
          "toPort" : 65535,
          "cidrIp" : "0.0.0.0/0"
        }
      ],
    )
    
    # LambdaSecurityGroup
    lambda_security_group = ec2.CfnSecurityGroup(self, "LambdaSecurityGroup",
      group_name = "labels-lambda-sg",
      group_description =  "HTTP traffic",
      vpc_id = core.Fn.import_value("VPC"),
      security_group_egress = [
        {
          "ipProtocol" : "tcp",
          "fromPort" : 0,
          "toPort" : 65535,
          "cidrIp" : "0.0.0.0/0"
        }
      ],
    )
    
    # Output
    core.CfnOutput(self, "WebServerInstanceProfileOutput",
      value = web_server_instance_profile.ref,
      description = "Web Server Instance Profile",
      export_name = "WebServerInstanceProfileOutput"
    )
    
    core.CfnOutput(self, "WebServerRoleOutput",
      value = web_server_role.attr_arn,
      description = "Web Server Role",
      export_name = "WebServerRoleOutput"
    )
    
    core.CfnOutput(self, "WebSecurityGroupOutput",
      value = web_security_group.ref,
      description = "Web Security Group",
      export_name = "WebSecurityGroupOutput"
    )
    
    core.CfnOutput(self, "LambdaSecurityGroupOutput",
      value = lambda_security_group.ref,
      description = "Lambda Security Group",
      export_name = "LambdaSecurityGroupOutput"
    )