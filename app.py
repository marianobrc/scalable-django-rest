#!/usr/bin/env python3
import os
import aws_cdk as cdk
from aws_cdk import (
    Environment,
)
from scalable_django_rest.pipeline_stack import MyDjangoApiPipelineStack


app = cdk.App()
pipeline = MyDjangoApiPipelineStack(
    app,
    "MyDjangoApiPipeline",
    repository="marianobrc/scalable-django-rest",
    branch="master",
    ssm_gh_connection_param="/Github/Connection",
    env=Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)
app.synth()
