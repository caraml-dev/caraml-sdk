import json
from datetime import datetime, timedelta
import pytest
import random
from sys import version_info
import uuid

import caraml.routers as turing
from caraml.routers.ensembler import PyFuncEnsembler
import caraml.routers.client.models
import caraml.routers.batch.config
import caraml.routers.batch.config.source
import caraml.routers.batch.config.sink
from caraml.routers.router.config.route import Route
from caraml.routers.router.config.router_config import RouterConfig, Protocol
from caraml.routers.router.config.autoscaling_policy import AutoscalingPolicy
from caraml.routers.router.config.traffic_rule import DefaultTrafficRule
from caraml.routers.router.config.resource_request import ResourceRequest
from caraml.routers.router.config.log_config import LogConfig, ResultLoggerType
from caraml.routers.router.config.enricher import Enricher
from caraml.routers.router.config.router_ensembler_config import (
    EnsemblerNopConfig,
    EnsemblerStandardConfig,
    DockerRouterEnsemblerConfig,
    PyfuncRouterEnsemblerConfig,
)
from caraml.routers.router.config.common.env_var import EnvVar
from caraml.routers.router.config.experiment_config import ExperimentConfig

from tests.caraml.routers.fixtures.mlflow import mock_mlflow
from tests.caraml.routers.fixtures.gcs import mock_gcs
from tests.caraml.routers import utils


@pytest.fixture
def turing_api() -> str:
    return "http://turing.local.svc:8080"


@pytest.fixture
def use_google_oauth() -> bool:
    return False


@pytest.fixture
def project():
    return caraml.routers.client.models.Project(
        id=10,
        name=f"project_name",
        mlflow_tracking_url="http://localhost:5000",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def active_project(responses, project):
    responses.add(
        method="GET",
        url=f"/api/v1/projects?name={project.name}",
        body=json.dumps([project], default=utils.json_serializer),
        match_querystring=True,
        status=200,
        content_type="application/json",
    )
    return project


@pytest.fixture
def projects(num_projects):
    return [
        caraml.routers.client.models.Project(
            id=i,
            name=f"project_{i}",
            mlflow_tracking_url="http://localhost:5000",
            created_at=datetime.now() + timedelta(seconds=i + 10),
            updated_at=datetime.now() + timedelta(seconds=i + 10),
        )
        for i in range(1, num_projects + 1)
    ]


@pytest.fixture
def generic_ensemblers(project, num_ensemblers):
    return [
        caraml.routers.client.models.GenericEnsembler(
            id=i,
            project_id=project.id,
            type=PyFuncEnsembler.TYPE,
            name=f"test_{i}",
            created_at=datetime.now() + timedelta(seconds=i + 10),
            updated_at=datetime.now() + timedelta(seconds=i + 10),
        )
        for i in range(1, num_ensemblers + 1)
    ]


@pytest.fixture
def nop_router_ensembler_config():
    return EnsemblerNopConfig(final_response_route_id="test")


@pytest.fixture
def standard_router_ensembler_config_with_experiment_mappings():
    return EnsemblerStandardConfig(
        experiment_mappings=[
            caraml.routers.client.models.EnsemblerStandardConfigExperimentMappings(
                experiment="experiment-1", treatment="treatment-1", route="route-1"
            ),
            caraml.routers.client.models.EnsemblerStandardConfigExperimentMappings(
                experiment="experiment-2", treatment="treatment-2", route="route-2"
            ),
        ],
        route_name_path=None,
        fallback_response_route_id="route-1",
        lazy_routing=False,
    )


@pytest.fixture
def standard_router_ensembler_config_with_route_name_path():
    return EnsemblerStandardConfig(
        experiment_mappings=None,
        route_name_path="route_name",
        fallback_response_route_id="route-1",
        lazy_routing=False,
    )


@pytest.fixture
def standard_router_ensembler_config_with_lazy_routing():
    return EnsemblerStandardConfig(
        experiment_mappings=None,
        route_name_path="route_name",
        fallback_response_route_id="route-1",
        lazy_routing=True,
    )


@pytest.fixture
def docker_router_ensembler_config():
    return DockerRouterEnsemblerConfig(
        image="test.io/just-a-test/turing-ensembler:0.0.0-build.0",
        resource_request=ResourceRequest(
            min_replica=1, max_replica=3, cpu_request="500m", memory_request="512Mi"
        ),
        endpoint=f"http://localhost:5000/ensembler_endpoint",
        timeout="500ms",
        port=5120,
        env=[],
    )


@pytest.fixture
def pyfunc_router_ensembler_config():
    return PyfuncRouterEnsemblerConfig(
        project_id=1,
        ensembler_id=1,
        resource_request=ResourceRequest(
            min_replica=1, max_replica=3, cpu_request="500m", memory_request="512Mi"
        ),
        timeout="500ms",
        env=[],
    )


@pytest.fixture
def bucket_name():
    return "bucket-name"


@pytest.fixture
def experiment_name(project, ensembler_name):
    return f"{project.name}/ensemblers/{ensembler_name}"


@pytest.fixture
def experiment_id():
    return random.randint(1, 100)


@pytest.fixture
def run_id():
    return uuid.uuid4().hex


@pytest.fixture
def artifact_uri(bucket_name, experiment_id, run_id):
    return f"gs://{bucket_name}/mlflow/{experiment_id}/{run_id}"


@pytest.fixture
def pyfunc_ensembler(project, ensembler_name, experiment_id, run_id, artifact_uri):
    return caraml.routers.client.models.PyFuncEnsembler(
        id=1,
        project_id=project.id,
        type=PyFuncEnsembler.TYPE,
        name=ensembler_name,
        mlflow_experiment_id=experiment_id,
        mlflow_run_id=run_id,
        artifact_uri=artifact_uri,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        python_version=f"{version_info.major}.{version_info.minor}.*",
    )


@pytest.fixture
def ensembling_job_config():
    source = caraml.routers.batch.config.source.BigQueryDataset(
        table="project.dataset.features",
        features=["feature_1", "feature_2", "features_3"],
    ).join_on(columns=["feature_1"])

    predictions = {
        "model_odd": caraml.routers.batch.config.source.BigQueryDataset(
            table="project.dataset.scores_model_odd",
            features=["feature_1", "prediction_score"],
        )
        .join_on(columns=["feature_1"])
        .select(columns=["prediction_score"]),
        "model_even": caraml.routers.batch.config.source.BigQueryDataset(
            query="""
                    SELECT feature_1, prediction_score
                    FROM `project.dataset.scores_model_even`
                    WHERE target_date = DATE("2021-03-15", "Asia/Jakarta")
                """,
            options={"viewsEnabled": "true", "materializationDataset": "my_dataset"},
        )
        .join_on(columns=["feature_1"])
        .select(columns=["prediction_score"]),
    }

    result_config = caraml.routers.batch.config.ResultConfig(
        type=routers.batch.config.ResultType.INTEGER, column_name="prediction_result"
    )

    sink = (
        caraml.routers.batch.config.sink.BigQuerySink(
            table="project.dataset.ensembling_results", staging_bucket="staging_bucket"
        )
        .save_mode(routers.batch.config.sink.SaveMode.OVERWRITE)
        .select(columns=["feature_1", "feature_2", "prediction_result"])
    )

    resource_request = caraml.routers.batch.config.ResourceRequest(
        driver_cpu_request="1",
        driver_memory_request="1G",
        executor_replica=5,
        executor_cpu_request="500Mi",
        executor_memory_request="800M",
    )

    return caraml.routers.batch.config.EnsemblingJobConfig(
        source=source,
        predictions=predictions,
        result_config=result_config,
        sink=sink,
        service_account="service-account",
        resource_request=resource_request,
    )


@pytest.fixture
def generic_router_status():
    return caraml.routers.client.models.RouterStatus(
        random.choice(["deployed", "undeployed", "failed", "pending"])
    )


@pytest.fixture
def generic_router_version_status():
    return caraml.routers.client.models.RouterVersionStatus(
        random.choice(["deployed", "undeployed", "failed", "pending"])
    )


@pytest.fixture
def generic_resource_request():
    return caraml.routers.client.models.ResourceRequest(
        min_replica=1, max_replica=3, cpu_request="100m", memory_request="512Mi"
    )


@pytest.fixture
def generic_log_level():
    return caraml.routers.client.models.LogLevel(
        random.choice(["DEBUG", "INFO", "WARN", "ERROR"])
    )


@pytest.fixture
def generic_result_logger_type():
    return caraml.routers.client.models.ResultLoggerType(
        random.choice(["nop", "upi", "bigquery", "kafka"])
    )


@pytest.fixture
def generic_bigquery_config():
    return caraml.routers.client.models.BigQueryConfig(
        table="bigqueryproject.bigquerydataset.bigquerytable",
        service_account_secret="my-little-secret",
    )


@pytest.fixture
def generic_kafka_config():
    return caraml.routers.client.models.KafkaConfig(
        brokers="1.2.3.4:5678,9.0.1.2:3456",
        topic="new_topics",
        serialization_format=random.choice(["json", "protobuf"]),
    )


@pytest.fixture(params=["kafka", "bigquery", "others"])
def log_config(
    generic_log_level,
    generic_result_logger_type,
    generic_bigquery_config,
    generic_kafka_config,
    request,
):
    result_logger_type = (
        generic_result_logger_type.value if request.param == "others" else request.param
    )

    params = dict(
        log_level=generic_log_level,
        custom_metrics_enabled=True,
        fiber_debug_log_enabled=True,
        jaeger_enabled=True,
        result_logger_type=caraml.routers.client.models.ResultLoggerType(
            result_logger_type
        ),
        bigquery_config=None,
        kafka_config=None,
    )

    if request.param == "kafka":
        params["kafka_config"] = generic_kafka_config
    elif request.param == "biggquery":
        params["bigquery_config"] = generic_bigquery_config

    return caraml.routers.client.models.RouterVersionLogConfig(**params)


@pytest.fixture
def generic_route():
    return caraml.routers.client.models.Route(
        id="model-a",
        type="PROXY",
        endpoint="http://predict_this.io/model-a",
        timeout="100ms",
    )


@pytest.fixture
def generic_route_grpc():
    return caraml.routers.client.models.Route(
        id="model-a-grpc",
        type="PROXY",
        endpoint="grpc_host:80",
        timeout="100ms",
        service_method="package/method",
    )


@pytest.fixture
def generic_traffic_rule_condition(
    generic_header_traffic_rule_condition, generic_payload_traffic_rule_condition
):
    field_source = random.choice(["header", "payload"])
    if field_source == "header":
        return generic_header_traffic_rule_condition
    elif field_source == "payload":
        return generic_payload_traffic_rule_condition


@pytest.fixture
def generic_header_traffic_rule_condition():
    return caraml.routers.client.models.TrafficRuleCondition(
        field_source=caraml.routers.client.models.FieldSource("header"),
        field="x-region",
        operator="in",
        values=["region-a", "region-b"],
    )


@pytest.fixture
def generic_payload_traffic_rule_condition():
    return caraml.routers.client.models.TrafficRuleCondition(
        field_source=caraml.routers.client.models.FieldSource("payload"),
        field="service_type.id",
        operator="in",
        values=["MyService", "YourService"],
    )


@pytest.fixture
def generic_traffic_rule(
    generic_header_traffic_rule_condition,
    generic_payload_traffic_rule_condition,
    generic_route,
):
    return caraml.routers.client.models.TrafficRule(
        name="generic-rule-name",
        conditions=[
            generic_header_traffic_rule_condition,
            generic_payload_traffic_rule_condition,
        ],
        routes=[generic_route.id],
    )


@pytest.fixture
def generic_ensembler_standard_config_with_experiment_mappings():
    return caraml.routers.client.models.EnsemblerStandardConfig(
        experiment_mappings=[
            caraml.routers.client.models.EnsemblerStandardConfigExperimentMappings(
                experiment="experiment-1", treatment="treatment-1", route="route-1"
            ),
            caraml.routers.client.models.EnsemblerStandardConfigExperimentMappings(
                experiment="experiment-2", treatment="treatment-2", route="route-2"
            ),
        ],
        lazy_routing=False,
    )


@pytest.fixture
def generic_ensembler_standard_config_with_route_name_path():
    return caraml.routers.client.models.EnsemblerStandardConfig(
        route_name_path="route_name", lazy_routing=False
    )


@pytest.fixture
def generic_ensembler_standard_config_lazy_routing():
    return caraml.routers.client.models.EnsemblerStandardConfig(
        route_name_path="route_name", lazy_routing=True
    )


@pytest.fixture
def generic_env_var():
    return caraml.routers.client.models.EnvVar(name="env_name", value="env_val")


@pytest.fixture
def generic_ensembler_docker_config(generic_resource_request, generic_env_var):
    return caraml.routers.client.models.EnsemblerDockerConfig(
        image="test.io/just-a-test/turing-ensembler:0.0.0-build.0",
        resource_request=generic_resource_request,
        endpoint=f"http://localhost:5000/ensembler_endpoint",
        timeout="500ms",
        port=5120,
        env=[generic_env_var],
        service_account="secret-name-for-google-service-account",
        autoscaling_policy=caraml.routers.client.models.AutoscalingPolicy(
            metric="memory", target="80"
        ),
    )


@pytest.fixture
def generic_ensembler_pyfunc_config(generic_resource_request, generic_env_var):
    return caraml.routers.client.models.EnsemblerPyfuncConfig(
        project_id=77,
        ensembler_id=11,
        resource_request=generic_resource_request,
        timeout="500ms",
        env=[generic_env_var],
        autoscaling_policy=caraml.routers.client.models.AutoscalingPolicy(
            metric="concurrency", target="10"
        ),
    )


@pytest.fixture(params=["standard", "docker", "pyfunc"])
def ensembler(
    request,
    generic_ensembler_standard_config_with_experiment_mappings,
    generic_ensembler_docker_config,
    generic_ensembler_pyfunc_config,
):
    ensembler_type = request.param
    return caraml.routers.client.models.RouterEnsemblerConfig(
        type=ensembler_type,
        standard_config=generic_ensembler_standard_config_with_experiment_mappings,
        docker_config=generic_ensembler_docker_config,
        pyfunc_config=generic_ensembler_pyfunc_config,
        created_at=datetime.now() + timedelta(seconds=10),
        updated_at=datetime.now() + timedelta(seconds=10),
    )


@pytest.fixture
def generic_standard_router_ensembler_config_with_experiment_mappings(
    generic_ensembler_standard_config_with_experiment_mappings,
):
    return caraml.routers.client.models.RouterEnsemblerConfig(
        type="standard",
        standard_config=generic_ensembler_standard_config_with_experiment_mappings,
    )


@pytest.fixture
def generic_standard_router_ensembler_config_with_route_name_path(
    generic_ensembler_standard_config_with_route_name_path,
):
    return caraml.routers.client.models.RouterEnsemblerConfig(
        type="standard",
        standard_config=generic_ensembler_standard_config_with_route_name_path,
    )


@pytest.fixture
def generic_standard_router_ensembler_config_lazy_routing(
    generic_ensembler_standard_config_lazy_routing,
):
    return caraml.routers.client.models.RouterEnsemblerConfig(
        type="standard",
        standard_config=generic_ensembler_standard_config_lazy_routing,
    )


@pytest.fixture
def generic_docker_router_ensembler_config(generic_ensembler_docker_config):
    return caraml.routers.client.models.RouterEnsemblerConfig(
        type="docker", docker_config=generic_ensembler_docker_config
    )


@pytest.fixture
def generic_pyfunc_router_ensembler_config(generic_ensembler_pyfunc_config):
    return caraml.routers.client.models.RouterEnsemblerConfig(
        type="pyfunc", pyfunc_config=generic_ensembler_pyfunc_config
    )


@pytest.fixture
def generic_enricher(generic_resource_request, generic_env_var):
    return caraml.routers.client.models.Enricher(
        id=1,
        image="test.io/just-a-test/turing-enricher:0.0.0-build.0",
        resource_request=generic_resource_request,
        endpoint=f"http://localhost:5000/enricher_endpoint",
        timeout="500ms",
        port=5180,
        env=[generic_env_var],
        service_account="service-account",
        autoscaling_policy=caraml.routers.client.models.AutoscalingPolicy(
            metric="rps", target="100"
        ),
    )


@pytest.fixture(params=["nop", "random_engine"])
def experiment_config(request):
    experiment_type = request.param
    if experiment_type == "nop":
        config = {}
    elif experiment_type == "random_engine":
        config = {
            "client": {"id": 1, "passkey": "abc"},
            "experiments": [{"client_id": 1, "name": "experiment_1"}],
            "variables": {
                "client_variables": [{"variable_name": "version", "required": False}]
            },
        }
    else:
        config = None

    return caraml.routers.client.models.ExperimentConfig(
        type=experiment_type, config=config
    )


@pytest.fixture
def generic_router_version(
    generic_router_version_status,
    generic_route,
    generic_traffic_rule,
    experiment_config,
    generic_resource_request,
    log_config,
    ensembler,
    generic_enricher,
):
    return caraml.routers.client.models.RouterVersion(
        id=2,
        created_at=datetime.now() + timedelta(seconds=20),
        updated_at=datetime.now() + timedelta(seconds=20),
        router=caraml.routers.client.models.Router(
            environment_name="test_env", name="test_router"
        ),
        version=1,
        status=generic_router_version_status,
        error="NONE",
        image="test.io/just-a-test/turing-router:0.0.0-build.0",
        routes=[generic_route for _ in range(2)],
        default_route_id=generic_route.id,
        rules=[generic_traffic_rule for _ in range(2)],
        experiment_engine=experiment_config,
        resource_request=generic_resource_request,
        timeout="100ms",
        log_config=log_config,
        protocol=caraml.routers.client.models.Protocol("HTTP_JSON"),
        ensembler=ensembler,
        monitoring_url="https://lookhere.io/",
        enricher=generic_enricher,
        autoscaling_policy=caraml.routers.client.models.AutoscalingPolicy(
            metric="cpu", target="90"
        ),
    )


@pytest.fixture
def generic_router_config(docker_router_ensembler_config):
    return RouterConfig(
        environment_name="id-dev",
        name="router-1",
        routes=[
            Route(
                id="model-a", endpoint="http://predict-this.io/model-a", timeout="100ms"
            ),
            Route(
                id="model-b", endpoint="http://predict-this.io/model-b", timeout="100ms"
            ),
        ],
        rules=None,
        default_route_id="model-a",
        experiment_engine=ExperimentConfig(
            type="test-exp",
            config={
                "variables": [
                    {"name": "order_id", "field": "fdsv", "field_source": "header"},
                    {"name": "country_code", "field": "dcsd", "field_source": "header"},
                    {"name": "latitude", "field": "d", "field_source": "header"},
                    {"name": "longitude", "field": "sdSDa", "field_source": "header"},
                ],
                "project_id": 102,
            },
        ),
        resource_request=ResourceRequest(
            min_replica=0, max_replica=2, cpu_request="500m", memory_request="512Mi"
        ),
        autoscaling_policy=AutoscalingPolicy(metric="cpu", target="90"),
        timeout="100ms",
        protocol=Protocol.HTTP,
        log_config=LogConfig(
            result_logger_type=ResultLoggerType.NOP,
            table="abc.dataset.table",
            service_account_secret="not-a-secret",
        ),
        enricher=Enricher(
            image="test.io/model-dev/echo:1.0.2",
            resource_request=ResourceRequest(
                min_replica=0, max_replica=2, cpu_request="500m", memory_request="512Mi"
            ),
            endpoint="/",
            timeout="60ms",
            port=8080,
            env=[EnvVar(name="test", value="abc")],
        ),
        ensembler=docker_router_ensembler_config,
    )


@pytest.fixture
def generic_router(project, generic_router_status, generic_router_version):
    return caraml.routers.client.models.RouterDetails(
        id=1,
        name="router-1",
        endpoint="http://localhost:5000/endpoint_1",
        environment_name="env_1",
        monitoring_url="http://localhost:5000/dashboard_1",
        project_id=project.id,
        status=generic_router_status,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        config=generic_router_version,
    )


@pytest.fixture
def generic_routers(
    project, num_routers, generic_router_status, generic_router_version
):
    return [
        caraml.routers.client.models.RouterDetails(
            id=i,
            name=f"router-{i}",
            endpoint=f"http://localhost:5000/endpoint_{i}",
            environment_name=f"env_{i}",
            monitoring_url=f"http://localhost:5000/dashboard_{i}",
            project_id=project.id,
            status=generic_router_status,
            created_at=datetime.now() + timedelta(seconds=i + 10),
            updated_at=datetime.now() + timedelta(seconds=i + 10),
            config=generic_router_version,
        )
        for i in range(1, num_routers + 1)
    ]


@pytest.fixture
def generic_events():
    return caraml.routers.client.models.RouterEvents(
        events=[
            caraml.routers.client.models.Event(
                created_at=datetime.now(),
                updated_at=datetime.now() + timedelta(seconds=1000),
                event_type="info",
                id=123,
                message="successfully deployed router not-a-router version 5",
                stage="deployment success",
                version=5,
            ),
            caraml.routers.client.models.Event(
                created_at=datetime.now() + timedelta(seconds=1500),
                updated_at=datetime.now() + timedelta(seconds=2500),
                event_type="error",
                id=124,
                message="failed to deploy router not-a-router version 5",
                stage="deployment failure",
                version=5,
            ),
        ]
    )


@pytest.fixture
def minimal_upi_router_config():
    return RouterConfig(
        name="sdk-router",
        routes=[
            Route(
                id="control",
                endpoint="grpc_host:80",
                timeout="50ms",
                service_method="caraml.upi.v1.UniversalPredictionService/PredictValues",
            ),
            Route(
                id="treatment-a",
                endpoint="grpc_host_2:80",
                timeout="50ms",
                service_method="caraml.upi.v1.UniversalPredictionService/PredictValues",
            ),
        ],
        timeout="10s",
        default_traffic_rule=DefaultTrafficRule(routes=["control"]),
        experiment_engine=ExperimentConfig(),
        protocol=Protocol.UPI,
    )
