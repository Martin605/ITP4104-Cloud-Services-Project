from aws_cdk import (
    aws_sns as sns,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_sqs as sqs,
    aws_s3 as s3,
    core
)


class SnssqsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
    
    
        # Set Parameters
        db_password_parameters = core.CfnParameter(self, "DBPassword",
            no_echo = True,
            description = "New account and RDS password",
            min_length = 1,
            max_length = 41,
            constraint_description = "the password must be between 1 and 41 characters",
            default = "DBPassword"
        )
        
        # LambdaExecutionRole
        LambdaExecutionRole = iam.CfnRole(self, "LabelsLambdaExecutionRole",
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
            managed_policy_arns = [
                "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
                "arn:aws:iam::aws:policy/AmazonRekognitionReadOnlyAccess",
                "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
                "arn:aws:iam::aws:policy/AWSXrayWriteOnlyAccess"
            ],
            policies = [
            {
                "policyName" : "root",
                "policyDocument" : {
                "Version":"2012-10-17",
                "Statement" : [
                {
                  "Effect": "Allow",
                  "Action" : [
                    "logs:*"
                  ],
                    "Resource": "arn:aws:logs:*:*:*"
                },
                ]}
            }]
        )
        
        # S3 Bucket
        source_bucket = "sourcebucketname%s" % (core.Aws.ACCOUNT_ID) 
        
        # LabelsLambda
        LabelsLambda = lambda_.CfnFunction(self, "LabelsLambda",
            handler = "lambda_function.lambda_handler",
            role = LambdaExecutionRole.attr_arn,
            code = {
                "s3Bucket" : source_bucket,
                "s3Key" : "lambda.zip"
            },
            runtime = "python3.6",
            timeout = 120,
            tracing_config = {
                "mode" : "Active"
            },
            vpc_config = {
                "securityGroupIds" : [core.Fn.import_value("LambdaSecurityGroupOutput")],
                "subnetIds" : [
                    core.Fn.import_value("PrivateSubnet1"),
                    core.Fn.import_value("PrivateSubnet2")
                ]
            },
            environment = {
                "variables" : {
                    "DATABASE_HOST" : core.Fn.import_value("MyDBEndpoint"),
                    "DATABASE_USER" : "web_user",
                    "DATABASE_PASSWORD" : db_password_parameters.value_as_string,
                    "DATABASE_DB_NAME" : "Photos"
                }
            }
        )
        
        # UploadQueue
        upload_queue = sqs.CfnQueue(self, "UploadQueue", 
            queue_name = "uploads-queue",
            message_retention_period = 12800,
            visibility_timeout = 300
        )
        
        # UploadSNSTopic
        upload_sns_topic = sns.CfnTopic(self, "UploadSNSTopic",
            display_name = "uploads-topic",
            subscription = [{
                "endpoint" : upload_queue.attr_arn,
                "protocol" : "sqs"
            },
            {
                "endpoint" : LabelsLambda.attr_arn,
                "protocol" : "lambda"
            }],
        )
        
        # QueuePolicy
        queue_policy = sqs.CfnQueuePolicy(self, "QueuePolicy", 
            queues = [upload_queue.ref],
            policy_document = {
                "Version" : "2012-10-17",
                "Id" : "QueuePolicy",
                "Statement" : [{
                    "Sid" : "Allow-SendMessage-To-Queues-From-SNS-Topic",
                    "Effect" : "Allow",
                    "Principal" : "*" ,
                    "Action" : [
                        "SQS:SendMessage"
                    ],
                    "Resource" : "*",
                    "Condition":{
                        "ArnEquals":{
                            "aws:SourceArn": "%s" % (upload_sns_topic.ref)
                        }
                    }
                }]
            }
        ) 

        # UploadTopicPolicy
        upload_topic_policy = sns.CfnTopicPolicy(self, "UploadTopicPolicy",
            policy_document = {
                "Version" : "2012-10-17",
                "Id" : "QueuePolicy",
                "Statement" : [{
                    "Sid" : "Allow-S3-Publish",
                    "Effect" : "Allow",
                    "Principal" : {
                        "Service": "s3.amazonaws.com"
                    },
                    "Action" : [
                        "SNS:Publish"
                    ],
                    "Resource" : upload_sns_topic.ref,
                    "Condition" : {
                        "StringEquals": {
                            "aws:SourceAccount": "!Sub '${AWS::AccountId}'"
                        },
                        "ArnLike" : {
                            "aws:SourceArn" : {
                                "Fn::Join" : [
                                    "",
                                    [
                                        "arn:aws:s3:*:*:",
                                        "!Sub 'imagebucketsns${AWS::AccountId}'"
                                    ]
                                ]
                            }
                        }
                    },
                }]
            },
            topics = [upload_sns_topic.ref]
        )

        # ImageS3Bucket
        image_s3_bucket = s3.CfnBucket(self, "ImageS3Bucket",
            bucket_name = "imagebucketsns%s" % (core.Aws.ACCOUNT_ID),
            notification_configuration = {
              "topicConfigurations" : [{
                "event" : 's3:ObjectCreated:*',
                "topic" : upload_sns_topic.ref
              }]
            }
        )
        image_s3_bucket.add_depends_on(upload_topic_policy)
        image_s3_bucket.apply_removal_policy(core.RemovalPolicy.DESTROY)

        # ImageS3BucketPermission
        ImageS3BucketPermission = lambda_.CfnPermission(self, "ImageS3BucketPermission",
          action = "lambda:InvokeFunction",
          function_name = LabelsLambda.attr_arn,
          principal = "sns.amazonaws.com",
          source_arn = upload_sns_topic.ref
        )
        
        # Outputs
        core.CfnOutput(self, "ImageS3BucketOutput",
            value = image_s3_bucket.ref,
            description = "Image S3 Bucket",
            export_name = "ImageS3Bucket"
        )
        
        core.CfnOutput(self, "LabelsLambdaOutput",
            value = LabelsLambda.ref,
            description = "Labels Lambda",
            export_name = "LabelsLambda"
        )