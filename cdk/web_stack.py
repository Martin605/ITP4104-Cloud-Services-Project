from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_logs as logs,
    aws_cloudformation as cloudformation,
    aws_elasticloadbalancingv2 as elasticloadbalancingv2,
    core
)

class WebStack(core.Construct):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Parameter
        SourceBucket = core.CfnParameter(
            self, "SourceBucket",
            type="String",
            default="default"
        )
        EC2VpcId = core.CfnParameter(
            self, "EC2VpcId",
            type="AWS::EC2::VPC::Id",
            default="vpc-a123baa3"
        )
        PrivateSubnet1 = core.CfnParameter(
            self, "PrivateSubnet1",
            type="AWS::EC2::Subnet::Id",
            default="subnet-456b351e"
        )
        PrivateSubnet2 = core.CfnParameter(
            self, "PrivateSubnet2",
            type="AWS::EC2::Subnet::Id",
            default="subnet-456b351e"
        )
        WebServerInstanceProfile = core.CfnParameter(
            self, "WebServerInstanceProfile",
            type="String",
            default="default"
        )
        WebServerRole = core.CfnParameter(
            self, "WebServerRole",
            type="String",
            default="default"
        )
        WebSecurityGroup = core.CfnParameter(
            self, "WebSecurityGroup",
            type="AWS::EC2::AWS::EC2::SecurityGroup::Id::Id",
            default="sg-a123fd85"
        )
        LoadBalancerArn = core.CfnParameter(
            self, "LoadBalancerArn",
            type="String",
            default="default"
        )
        LatestAmiId = core.CfnParameter(
            self, "LatestAmiId",
            description="AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>",
            default="/aws/service/ami-amazon-linux-latest/amzn-ami-hvm-x86_64-gp2"
        )

        # Resources
        CloudFormationLogs = logs.LogGroup(
            self, 'CloudFormationLogs', retention=logs.RetentionDays('ONE_WEEK'))

        WebInstance1 = ec2.CfnInstance(
            self, 'WebInstance1', additional_info=None, affinity=None,
            iam_instance_profile=WebServerInstanceProfile.value_as_string,
            image_id=LatestAmiId.value_as_string,
            instance_type='t3.micro',
            network_interfaces=[
                {
                    "deviceIndex":"0",
                    "groupSet": [WebSecurityGroup.value_as_string],
                    "subnetId": PrivateSubnet1.value_as_string
                }
            ],
            tags=[core.CfnTag(key="Name", value="WebServer1")],
            user_data=core.Fn.base64(
            """#!/bin/bash -ex
            yum update -y
            /opt/aws/bin/cfn-init -v --stack {StackName} --resource WebInstance1 --configsets InstallAndDeploy --region {Region}
            # Signal the status from cfn-init (via $?)
            /opt/aws/bin/cfn-signal -e $? --stack {StackName} --resource WebInstance1 --region {Region}
            """.format(StackName=core.Aws.STACK_NAME,Region=core.Aws.REGION)
            )
        )
        WebInstance1.cfn_options.metadata = {
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "type": "S3",
                    "buckets": [
                        SourceBucket.value_as_string
                    ],
                    "roleName": WebServerRole.value_as_string
                }
            },
            "AWS::CloudFormation::Init": {
                "configSets": {
                    "InstallAndDeploy": [
                        "Install",
                        "InstallLogs",
                        "Deploy"
                    ]
                },
                "Install": {
                    "packages": {
                        "yum": {
                            "python36": [],
                            "python36-devel": [],
                            "nginx": [],
                            "gcc": []
                        }
                    },
                    "files": {
                        "/etc/cfn/cfn-hup.conf": {
                            "content": """
                                [main]
                                stack={}
                                region={}
                                interval=1
                                verbose=true""".format(core.Aws.STACK_ID, core.Aws.REGION),
                            "mode": "000400",
                            "owner": "root",
                            "group": "root"
                        },
                        "/etc/cfn/hooks.d/cfn-auto-reloader.conf": {
                            "content": """
                                [cfn-auto-reloader-hook]
                                triggers=post.update
                                path=Resources.WebInstance1.Metadata.AWS::CloudFormation::Init
                                action=/opt/aws/bin/cfn-init -v --stack {} --resource WebInstance1 --configsets InstallAndDeploy --region {}
                                runas=root""".format(core.Aws.STACK_NAME, core.Aws.REGION),
                            "mode": "000400",
                            "owner": "root",
                            "group": "root"
                        }
                    },
                    "services": {
                        "sysvinit": {
                            "nginx": {
                                "enabled": "true",
                                "ensureRunning": "true"
                            },
                            "cfn-hup": {
                                "enabled": "true",
                                "ensureRunning": "true",
                                "files": [
                                    "/etc/cfn/cfn-hup.conf",
                                    "/etc/cfn/hooks.d/cfn-auto-reloader.conf"
                                ]
                            }
                        }
                    },
                    "commands": {
                        "01_unblock_nginx": {
                            "command": "chkconfig nginx on"
                        },
                        "02_install_xray": {
                            "command": "curl https://s3.dualstack.us-east-2.amazonaws.com/aws-xray-assets.us-east-2/xray-daemon/aws-xray-daemon-3.x.rpm -o /tmp/xray.rpm && yum install -y /tmp/xray.rpm\n",
                            "cwd": "/tmp",
                            "ignoreErrors": "true"
                        }
                    }
                },
                "InstallLogs": {
                    "packages": {
                        "yum": {
                            "awslogs": []
                        }
                    },
                    "files": {
                        "/etc/awslogs/awslogs.conf": {
                            "content": """
                            [general]
                            state_file= /var/awslogs/state/agent-state
                            [yum]
                            file = /var/log/yum.log
                            log_group_name = %s
                            log_stream_name = {{hostname}} - {{instance_id}} yum.log
                            [messages]
                            file = /var/log/messages
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} messages.log
                            [cfn-hup]
                            file = /var/log/cfn-hup.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} cfn-hup.log
                            [cfn-init]
                            file = /var/log/cfn-init.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} cfn-init.log
                            [cfn-init-cmd]
                            file = /var/log/cfn-init-cmd.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} cfn-init-cmd.log
                            [cloud-init]
                            file = /var/log/cloud-init.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} cloud-init.log
                            [cloud-init-output]
                            file = /var/log/cloud-init-output.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} cloud-init.log
                            [handler]
                            file = /var/log/handler.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} handler.log

                            [uwsgi]
                            file = /var/log/uwsgi.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} uwsgi.log
                            [nginx_access]
                            file = /var/log/nginx/access.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} nginx_access.log
                            [nginx_error]
                            file = /var/log/nginx/error.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} nginx_error.log
                            """.format(CloudFormationLogs=CloudFormationLogs.log_group_name),
                            "group": "root",
                            "owner": "root",
                            "mode": "000400"
                        },
                        "/etc/awslogs/awscli.conf": {
                            "content": """
                                [plugins]
                                cwlogs = cwlogs
                                [default]
                                region = {}
                            """.format(core.Aws.REGION),
                            "mode": "000444",
                            "owner": "root",
                            "group": "root"
                        }
                    },
                    "commands": {
                        "01_create_state_directory": {
                            "command": "mkdir -p /var/awslogs/state"
                        }
                    },
                    "services": {
                        "sysvinit": {
                            "awslogs": {
                                "enabled": "true",
                                "ensureRunning": "true",
                                "files": [
                                    "/etc/awslogs/awslogs.conf"
                                ]}
                        }
                    }
                },
                "Deploy": {
                    "sources": {
                        "/photos": "https://s3.amazonaws.com/{}/deploy-app.zip".format(SourceBucket.value_as_string)
                    },
                    "commands": {
                        "01_pip_uwsgi": {
                            "command": "pip-3.6 install uwsgi",
                            "cwd": "/photos",
                            "ignoreErrors": "false"
                        },
                        "02_pip_flask_app_requirements": {
                            "command": "pip-3.6 install -r requirements.txt",
                            "cwd": "/photos/FlaskApp",
                            "ignoreErrors": "false"
                        },
                        "03_stop_uwsgi": {
                            "command": "stop uwsgi",
                            "ignoreErrors": "true"
                        },
                        "04_stop_nginx": {
                            "command": "service nginx stop"
                        },
                        "05_copy_config": {
                            "command": "mv -f nginx.conf /etc/nginx/nginx.conf && mv -f uwsgi.conf /etc/init/uwsgi.conf",
                            "cwd": "/photos/Deploy",
                            "ignoreErrors": "false"
                        },
                        "06_create_database": {
                            "command": "python3 database_create_tables.py",
                            "cwd": "/photos/Deploy",
                            "ignoreErrors": "false"
                        },
                        "07_start_uwsgi": {
                            "command": "start uwsgi"
                        },
                        "08_restart_nginx": {
                            "command": "service nginx start"
                        }
                    }
                }
            }
        }
        WebInstance1.cfn_options.creation_policy = core.CfnCreationPolicy(
            resource_signal=core.CfnResourceSignal(timeout='PT10M'))

        WebInstance2 = ec2.CfnInstance(
            self, 'WebInstance2', additional_info=None, affinity=None,
            iam_instance_profile=WebServerInstanceProfile.value_as_string,
            image_id=LatestAmiId.value_as_string,
            instance_type='t3.micro',
            network_interfaces=[
                {
                    "deviceIndex":"0",
                    "groupSet": [WebSecurityGroup.value_as_string],
                    "subnetId": PrivateSubnet2.value_as_string
                }
            ],
            tags=[core.CfnTag(key="Name", value="WebServer2")],
            user_data=core.Fn.base64(
            """#!/bin/bash -ex
              yum update -y
              /opt/aws/bin/cfn-init -v --stack {StackName} --resource WebInstance2 --configsets InstallAndDeploy --region {Region}
              # Signal the status from cfn-init (via $?)
              /opt/aws/bin/cfn-signal -e $? --stack {StackName} --resource WebInstance2 --region {Region}
            """.format(StackName=core.Aws.STACK_NAME,Region=core.Aws.REGION)
            )
        )
        WebInstance2.cfn_options.metadata = {
            "AWS::CloudFormation::Authentication": {
                "rolebased": {
                    "type": "S3",
                    "buckets": [
                        SourceBucket.value_as_string
                    ],
                    "roleName": WebServerRole.value_as_string
                }
            },
            "AWS::CloudFormation::Init": {
                "configSets": {
                    "InstallAndDeploy": [
                        "Install",
                        "InstallLogs",
                        "Deploy"
                    ]
                },
                "Install": {
                    "packages": {
                        "yum": {
                            "python36": [],
                            "python36-devel": [],
                            "nginx": [],
                            "gcc": []
                        }
                    },
                    "files": {
                        "/etc/cfn/cfn-hup.conf": {
                            "content": """
                                [main]
                                stack={}
                                region={}
                                interval=1
                                verbose=true""".format(core.Aws.STACK_ID, core.Aws.REGION),
                            "mode": "000400",
                            "owner": "root",
                            "group": "root"
                        },
                        "/etc/cfn/hooks.d/cfn-auto-reloader.conf": {
                            "content": """
                                [cfn-auto-reloader-hook]
                                triggers=post.update
                                path=Resources.WebInstance1.Metadata.AWS::CloudFormation::Init
                                action=/opt/aws/bin/cfn-init -v --stack {} --resource WebInstance2 --configsets InstallAndDeploy --region {}
                                runas=root""".format(core.Aws.STACK_NAME, core.Aws.REGION),
                            "mode": "000400",
                            "owner": "root",
                            "group": "root"
                        }
                    },
                    "services": {
                        "sysvinit": {
                            "nginx": {
                                "enabled": "true",
                                "ensureRunning": "true"
                            },
                            "cfn-hup": {
                                "enabled": "true",
                                "ensureRunning": "true",
                                "files": [
                                    "/etc/cfn/cfn-hup.conf",
                                    "/etc/cfn/hooks.d/cfn-auto-reloader.conf"
                                ]
                            }
                        }
                    },
                    "commands": {
                        "01_unblock_nginx": {
                            "command": "chkconfig nginx on"
                        },
                        "02_install_xray": {
                            "command": "curl https://s3.dualstack.us-east-2.amazonaws.com/aws-xray-assets.us-east-2/xray-daemon/aws-xray-daemon-3.x.rpm -o /tmp/xray.rpm && yum install -y /tmp/xray.rpm\n",
                            "cwd": "/tmp",
                            "ignoreErrors": "true"
                        }
                    }
                },
                "InstallLogs": {
                    "packages": {
                        "yum": {
                            "awslogs": []
                        }
                    },
                    "files": {
                        "/etc/awslogs/awslogs.conf": {
                            "content": """
                            [general]
                            state_file= /var/awslogs/state/agent-state
                            [yum]
                            file = /var/log/yum.log
                            log_group_name = %s
                            log_stream_name = {{hostname}} - {{instance_id}} yum.log
                            [messages]
                            file = /var/log/messages
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} messages.log
                            [cfn-hup]
                            file = /var/log/cfn-hup.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} cfn-hup.log
                            [cfn-init]
                            file = /var/log/cfn-init.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} cfn-init.log
                            [cfn-init-cmd]
                            file = /var/log/cfn-init-cmd.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} cfn-init-cmd.log
                            [cloud-init]
                            file = /var/log/cloud-init.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} cloud-init.log
                            [cloud-init-output]
                            file = /var/log/cloud-init-output.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} cloud-init.log
                            [handler]
                            file = /var/log/handler.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} handler.log

                            [uwsgi]
                            file = /var/log/uwsgi.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} uwsgi.log
                            [nginx_access]
                            file = /var/log/nginx/access.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} nginx_access.log
                            [nginx_error]
                            file = /var/log/nginx/error.log
                            log_group_name = {CloudFormationLogs}
                            log_stream_name = {{hostname}} - {{instance_id}} nginx_error.log
                            """.format(CloudFormationLogs=CloudFormationLogs.log_group_name),
                            "group": "root",
                            "owner": "root",
                            "mode": "000400"
                        },
                        "/etc/awslogs/awscli.conf": {
                            "content": """
                                [plugins]
                                cwlogs = cwlogs
                                [default]
                                region = {}
                            """.format(core.Aws.REGION),
                            "mode": "000444",
                            "owner": "root",
                            "group": "root"
                        }
                    },
                    "commands": {
                        "01_create_state_directory": {
                            "command": "mkdir -p /var/awslogs/state"
                        }
                    },
                    "services": {
                        "sysvinit": {
                            "awslogs": {
                                "enabled": "true",
                                "ensureRunning": "true",
                                "files": [
                                    "/etc/awslogs/awslogs.conf"
                                ]}
                        }
                    }
                },
                "Deploy": {
                    "sources": {
                        "/photos": "https://s3.amazonaws.com/{}/deploy-app.zip".format(SourceBucket.value_as_string)
                    },
                    "commands": {
                        "01_pip_uwsgi": {
                            "command": "pip-3.6 install uwsgi",
                            "cwd": "/photos",
                            "ignoreErrors": "false"
                        },
                        "02_pip_flask_app_requirements": {
                            "command": "pip-3.6 install -r requirements.txt",
                            "cwd": "/photos/FlaskApp",
                            "ignoreErrors": "false"
                        },
                        "03_stop_uwsgi": {
                            "command": "stop uwsgi",
                            "ignoreErrors": "true"
                        },
                        "04_stop_nginx": {
                            "command": "service nginx stop"
                        },
                        "05_copy_config": {
                            "command": "mv -f nginx.conf /etc/nginx/nginx.conf && mv -f uwsgi.conf /etc/init/uwsgi.conf",
                            "cwd": "/photos/Deploy",
                            "ignoreErrors": "false"
                        },
                        "06_create_database": {
                            "command": "python3 database_create_tables.py",
                            "cwd": "/photos/Deploy",
                            "ignoreErrors": "false"
                        },
                        "07_start_uwsgi": {
                            "command": "start uwsgi"
                        },
                        "08_restart_nginx": {
                            "command": "service nginx start"
                        }
                    }
                }
            }
        }

        WebInstance2.cfn_options.creation_policy = core.CfnCreationPolicy(
            resource_signal=core.CfnResourceSignal(timeout='PT10M'))

        DefaultTargetGroup = elasticloadbalancingv2.CfnTargetGroup(
            self, 'DefaultTargetGroup',
            health_check_interval_seconds=15,
            health_check_path="/",
            health_check_protocol="HTTP",
            health_check_timeout_seconds=10,
            healthy_threshold_count=2,
            unhealthy_threshold_count=2,
            matcher={'httpCode': '200-299'},
            port=80,
            protocol="HTTP",
            vpc_id=EC2VpcId.value_as_string,
            target_group_attributes=[
                {"key": "deregistration_delay.timeout_seconds",
                 "value": "30"}],
            targets=[
                {"id":WebInstance1.ref,"port":80},
                {"id":WebInstance2.ref,"port":80}
            ]
        )

        HttpListener = elasticloadbalancingv2.CfnListener(
            self, 'HttpListener',
            default_actions=[{
                "type": "forward",
                "targetGroupArn": DefaultTargetGroup.ref
            }],
            load_balancer_arn=LoadBalancerArn.value_as_string,
            port=80,
            protocol="HTTP")
