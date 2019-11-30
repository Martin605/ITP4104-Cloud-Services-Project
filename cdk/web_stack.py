from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_logs as logs,
    aws_cloudformation as cloudformation,
    core
)


class WebStack(core.Construct):

    def __init__(self, scope: core.Construct, id: str,
                 ec2_vpc_id, private_subnet_1, private_subnet_2,
                 web_server_instance_profile, web_server_role,
                 web_security_group, load_balancer_arn, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        latest_ami_id_parameters = core.CfnParameter(self, "LatestAmiId",
                                                     description="AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>",
                                                     default="/aws/service/ami-amazon-linux-latest/amzn-ami-hvm-x86_64-gp2"
                                                     )

        cloudFformation_logs = logs.LogGroup(
            self, 'CloudFormationLogs', retention=logs.RetentionDays('SEVEN_DAYS'))

        web_instance_1 = ec2.CfnInstance(
            self, 'WebInstance1', additional_info=None, affinity=None,
            iam_instance_profile=web_server_instance_profile,
            image_id=latest_ami_id_parameters.ref,
            instance_type='t3.micro',
            network_interfaces=[
                ec2.CfnNetworkInterface(self,
                                        'WebInstance1NetworkInterfaces',
                                        subnet_id=private_subnet_1.ref,
                                        group_set=web_security_group.ref
                                        )
            ],

            tags=[
                core.CfnTag(
                    key="Name",
                    Value="WebServer1")
            ],
            tenancy=None,
            user_data="""
            #!/bin/bash -ex
            yum update -y
            /opt/aws/bin/cfn-init -v --stack ${StackName} --resource WebInstance1 --configsets InstallAndDeploy --region ${Region}
            # Signal the status from cfn-init (via $?)
            /opt/aws/bin/cfn-signal -e $? --stack ${StackName} --resource WebInstance1 --region ${Region}
            """)
        web_instance_1.cfn_options.metadata = {
            "AWS::CloudFormation::Authentication": {
                "AWS::CloudFormation::Authentication": {
                    "type": "S3",
                    "buckets": {SourceBucket},
                    "roleName": WebServerRole
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
                            "content": null,
                            "mode": "000400",
                            "owner": "root",
                            "group": "root"
                        },
                        "/etc/cfn/hooks.d/cfn-auto-reloader.conf": {
                            "content": null,
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
                            "content": null,
                            "group": "root",
                            "owner": "root",
                            "mode": "000400"
                        },
                        "/etc/awslogs/awscli.conf": {
                            "content": null,
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
                                ]
                            }
                        }
                    }
                },
                "Deploy": {
                    "sources": {
                        "/photos": null
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
        web_instance_1.cfn_options.creation_policy = core.CfnCreationPolicy(
            self, resource_signal=core.CfnResourceSignal(count=None, timeout='PT10M'))
