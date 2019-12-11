#!/usr/bin/env python3

from aws_cdk import core

from cdk.cdk_stack import CdkStack
from cdk.vpc_stack import VpcStack
from cdk.iam_stack import IAMStack
from cdk.parameter_stack import ParametersStack
from cdk.cognito_stack import CognitoStack
from cdk.cloud9_stack import Cloud9Stack
from cdk.security_stack import SecurityStack
from cdk.cdn_stack import CdnStack
from cdk.db_stack import DBStack
from cdk.snssqs_stack import SnssqsStack
from cdk.web_stack import WebStack

app = core.App()
CdkStack(app, "cdk")
VpcStack(app, "VpcStack")
IAMStack(app, "IAMStack")
ParametersStack(app, "ParametersStack")
CognitoStack(app, "CognitoStack")
SecurityStack(app, "SecurityStack")
Cloud9Stack(app, "Cloud9Stack")
CdnStack(app, "CdnStack")
DBStack(app, "DBStack")
SnssqsStack(app, "SnssqsStack")
WebStack(app, "WebStack")
app.synth()
