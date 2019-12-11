#!/usr/bin/env python3

from aws_cdk import core

from cdk.cdk_stack import CdkStack
from cdk.vpc_stack import VpcStack
from cdk.iam_stack import IAMStack
from cdk.cloud9_stack import Cloud9Stack
from cdk.security_stack import SecurityStack
from cdk.cdn_stack import CdnStack
from cdk.parameter_stack import ParametersStack
from cdk.db_stack import DBStack
from cdk.cognito_stack import CognitoStack
from cdk.snssqs_stack import SnssqsStack

app = core.App()
CdkStack(app, "cdk")
VpcStack(app, "VpcStack")
IAMStack(app, "IAMStack")
Cloud9Stack(app, "Cloud9Stack")
SecurityStack(app, "SecurityStack")
CdnStack(app, "CdnStack")
ParametersStack(app, "ParametersStack")
DBStack(app, "DBStack")
SnssqsStack(app, "SnssqsStack")
CognitoStack(app, "CognitoStack")
app.synth()
