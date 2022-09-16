from constructs import Construct
from aws_cdk import (
    Stack,
    pipelines as pipelines,
    aws_ssm as ssm,
    aws_secretsmanager as secretsmanager,
    aws_rds as rds,
)
from .deployment_stage import MyDjangoApiPipelineStage


class MyDjangoApiPipelineStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        repository: str,
        branch: str,
        ssm_gh_connection_param: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.repository = repository
        self.branch = branch
        self.ssm_gh_connection_param = ssm_gh_connection_param
        self.gh_connection_arn = ssm.StringParameter.value_for_string_parameter(
            self, ssm_gh_connection_param
        )
        aws_env = kwargs.get("env")
        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            docker_credentials=[
                pipelines.DockerCredential.docker_hub(
                    secretsmanager.Secret.from_secret_name_v2(
                        self,
                        "DockerHubSecret",
                        secret_name="/MyDjangoApiPipeline/DockerHubSecret",
                    )
                ),
            ],
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.connection(
                    self.repository,
                    self.branch,
                    connection_arn=self.gh_connection_arn,
                    trigger_on_push=True,
                ),
                commands=[
                    "npm install -g aws-cdk",  # Installs the cdk cli on Codebuild
                    "pip install -r requirements.txt",  # Instructs Codebuild to install required packages
                    "npx cdk synth MyDjangoApiPipeline",
                ],
            ),
        )
        # Deploy to a staging environment
        self.staging_env = MyDjangoApiPipelineStage(
            self,
            "MyDjangoApiStaging",
            env=aws_env,  # AWS Account and Region
            django_settings_module="app.settings.stage",
            django_debug=True,
            domain_name="scalabledjango.com",
            subdomain="stage",
            # Limit scaling in staging to reduce costs
            db_min_capacity=rds.AuroraCapacityUnit.ACU_2,
            db_max_capacity=rds.AuroraCapacityUnit.ACU_2,
            db_auto_pause_minutes=5,
            app_task_min_scaling_capacity=1,
            app_task_max_scaling_capacity=2,
        )
        pipeline.add_stage(self.staging_env)
        # Deploy to production after manual approval
        self.production_env = MyDjangoApiPipelineStage(
            self,
            "MyDjangoApiProduction",
            env=aws_env,  # AWS Account and Region
            django_settings_module="app.settings.prod",
            django_debug=False,
            domain_name="scalabledjango.com",
            db_auto_pause_minutes=0,  # Keep the database always up in production
            app_task_min_scaling_capacity=2,
            app_task_max_scaling_capacity=5,
        )
        pipeline.add_stage(
            self.production_env,
            pre=[pipelines.ManualApprovalStep("PromoteToProduction")],
        )
