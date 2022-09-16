import os
from constructs import Construct
from aws_cdk import (
    Stage,
    aws_rds as rds,
)
from scalable_django_rest.network_stack import NetworkStack
from scalable_django_rest.database_stack import DatabaseStack
from scalable_django_rest.django_api_stack import MyDjangoAPI
from scalable_django_rest.static_files_stack import StaticFilesStack
from scalable_django_rest.external_secrets_stack import ExternalSecretsStack
from scalable_django_rest.dns_route_to_alb_stack import DnsRouteToAlbStack


class MyDjangoApiPipelineStage(Stage):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        django_settings_module: str,
        django_debug: bool,
        domain_name: str,
        subdomain: str = None,
        db_min_capacity: rds.AuroraCapacityUnit = rds.AuroraCapacityUnit.ACU_2,
        db_max_capacity: rds.AuroraCapacityUnit = rds.AuroraCapacityUnit.ACU_4,
        db_auto_pause_minutes: int = 0,
        app_task_min_scaling_capacity: int = 2,
        app_task_max_scaling_capacity: int = 4,
        **kwargs,
    ):

        super().__init__(scope, construct_id, **kwargs)
        self.django_settings_module = django_settings_module
        self.django_debug = django_debug
        self.domain_name = domain_name
        self.subdomain = subdomain
        self.db_min_capacity = db_min_capacity
        self.db_max_capacity = db_max_capacity
        self.db_auto_pause_minutes = db_auto_pause_minutes
        self.app_task_min_scaling_capacity = app_task_min_scaling_capacity
        self.app_task_max_scaling_capacity = app_task_max_scaling_capacity
        aws_env = kwargs.get("env")
        self.network = NetworkStack(
            self,
            "Network",
            env=aws_env,  # AWS Account and Region
        )
        self.database = DatabaseStack(
            self,
            "Database",
            env=aws_env,  # AWS Account and Region
            vpc=self.network.vpc,
            database_name="app_db",
            min_capacity=self.db_min_capacity,
            max_capacity=self.db_max_capacity,
            auto_pause_minutes=self.db_auto_pause_minutes,
        )
        # Serve static files for the Backoffice (django-admin)
        self.static_files = StaticFilesStack(
            self,
            "StaticFiles",
            env=aws_env,  # AWS Account and Region
            cors_allowed_origins=[
                f"https://{self.subdomain}.{self.domain_name}"
                if self.subdomain
                else f"https://{self.domain_name}"
            ],
        )
        self.app_env_vars = {
            "DJANGO_SETTINGS_MODULE": self.django_settings_module,
            "DJANGO_DEBUG": str(self.django_debug),
            "AWS_ACCOUNT_ID": os.getenv("CDK_DEFAULT_ACCOUNT"),
            "AWS_STATIC_FILES_BUCKET_NAME": self.static_files.s3_bucket.bucket_name,
            "AWS_STATIC_FILES_CLOUDFRONT_URL": self.static_files.cloudfront_distro.distribution_domain_name,
        }
        self.secrets = ExternalSecretsStack(
            self,
            "ExternalParameters",
            env=aws_env,  # AWS Account and Region
            name_prefix=f"/{self.stage_name}/",
            database_secrets=self.database.aurora_serverless_db.secret,
        )
        self.django_app = MyDjangoAPI(
            self,
            "APIService",
            env=aws_env,  # AWS Account and Region
            vpc=self.network.vpc,
            ecs_cluster=self.network.ecs_cluster,
            queue=self.queues.default_queue,
            env_vars=self.app_env_vars,
            secrets=self.secrets.app_secrets,
            task_cpu=256,
            task_memory_mib=512,
            task_desired_count=self.app_task_min_scaling_capacity,
            task_min_scaling_capacity=self.app_task_min_scaling_capacity,
            task_max_scaling_capacity=self.app_task_max_scaling_capacity,
        )
        # Route requests made in the domain to the ALB
        self.dns = DnsRouteToAlbStack(
            self,
            "DnsToAlb",
            env=aws_env,  # AWS Account and Region
            domain_name=self.domain_name,
            subdomain=self.subdomain,
            alb=self.django_app.alb_fargate_service.load_balancer,
        )
