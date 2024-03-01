import pytest
import caraml.routers.batch.config.source
import caraml.routers.batch.config.sink
import caraml.routers.client.models

from caraml.routers.client.model.env_var import EnvVar


@pytest.mark.parametrize(
    "source,predictions,result_config,sink,expected_fn",
    [
        pytest.param(
            routers.batch.config.source.BigQueryDataset(
                table="project.table.dataset_1",
                features=["feature_1", "feature_2", "feature_3"],
            ).join_on(columns=["feature_2", "feature_3"]),
            {
                "model_a": routers.batch.config.source.BigQueryDataset(
                    table="project.table.model_a_results",
                    features=["feature_2", "feature_3", "prediction"],
                )
                .join_on(["feature_2", "feature_3"])
                .select(["prediction"])
            },
            routers.batch.config.ResultConfig(
                type=routers.batch.config.ResultType.FLOAT,
                column_name="ensembling_result",
            ),
            (
                routers.batch.config.sink.BigQuerySink(
                    table="project.table.ensembling_results",
                    staging_bucket="staging_bucket",
                    options={},
                )
                .select(["feature_1", "ensembling_result"])
                .save_mode(routers.batch.config.sink.SaveMode.IGNORE)
            ),
            lambda source, predictions, result_config, sink: routers.client.models.EnsemblingJobSpec(
                source=source.to_open_api(),
                predictions={
                    name: source.to_open_api() for name, source in predictions.items()
                },
                ensembler=routers.client.models.EnsemblingJobEnsemblerSpec(
                    result=result_config.to_open_api()
                ),
                sink=sink.to_open_api(),
            ),
            id="Initialize ensembling job spec",
        )
    ],
)
def test_job_spec(source, predictions, result_config, sink, expected_fn):
    job_config = routers.batch.config.EnsemblingJobConfig(
        source=source,
        predictions=predictions,
        result_config=result_config,
        sink=sink,
        service_account="",
    )
    expected = expected_fn(source, predictions, result_config, sink)
    assert job_config.job_spec() == expected


@pytest.mark.parametrize(
    "service_account,resource_request,env_vars,expected_fn",
    [
        pytest.param(
            "service-account@gcp-project.iam.gserviceaccount.com",
            routers.batch.config.ResourceRequest(
                driver_cpu_request="1",
                driver_memory_request="1G",
                executor_replica=5,
                executor_cpu_request="500Mi",
                executor_memory_request="800M",
            ),
            {"SOME_VAR": "SOME_VALUE"},
            lambda service_account, resource_request, env_vars: routers.client.models.EnsemblerInfraConfig(
                service_account_name=service_account,
                resources=resource_request,
                env=[
                    EnvVar(name=name, value=value) for name, value in env_vars.items()
                ],
            ),
            id="Initialize ensembling job infra spec",
        ),
        pytest.param(
            "service-account@gcp-project.iam.gserviceaccount.com",
            None,
            {"SOME_VAR": "SOME_VALUE"},
            lambda service_account, resource_request, env_vars: routers.client.models.EnsemblerInfraConfig(
                service_account_name=service_account,
                resources=resource_request,
                env=[
                    EnvVar(name=name, value=value) for name, value in env_vars.items()
                ],
            ),
            id="Initialize ensembling job with default resource request",
        ),
    ],
)
def test_infra_spec(service_account, resource_request, env_vars, expected_fn):
    job_config = routers.batch.config.EnsemblingJobConfig(
        source=None,
        predictions={},
        result_config=None,
        sink=None,
        service_account=service_account,
        resource_request=resource_request,
        env_vars=env_vars,
    )
    expected = expected_fn(service_account, resource_request, env_vars)
    assert job_config.infra_spec() == expected
