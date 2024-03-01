# Copyright 2020 The Merlin Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import os
from tests.caraml.models.utils import undeploy_all_version
from time import sleep

import pandas as pd
import pytest
from caraml.models.logger import Logger, LoggerConfig, LoggerMode
from caraml.models.model import ModelType
from caraml.models.resource_request import ResourceRequest
from caraml.models.transformer import StandardTransformer, Transformer
from recursive_diff import recursive_eq

import caraml.models as merlin
from caraml.models import DeploymentMode, MetricsType

request_json = {"instances": [[2.8, 1.0, 6.8, 0.4], [3.1, 1.4, 4.5, 1.6]]}
tensorflow_request_json = {
    "signature_name": "predict",
    "instances": [
        {
            "sepal_length": 2.8,
            "sepal_width": 1.0,
            "petal_length": 6.8,
            "petal_width": 0.4,
        },
        {
            "sepal_length": 0.1,
            "sepal_width": 0.5,
            "petal_length": 1.8,
            "petal_width": 2.4,
        },
    ],
}


@pytest.mark.integration
@pytest.mark.dependency()
def test_model_version_with_labels(
    integration_test_url, project_name, use_google_oauth
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model("sklearn-labels", ModelType.SKLEARN)

    model_dir = "tests/caraml/models/sklearn-model"

    undeploy_all_version()

    with merlin.new_model_version(labels={"model": "T-800"}) as v:
        # Upload the serialized model to MLP
        merlin.log_model(model_dir=model_dir)
        assert len(v.labels) == 1
        assert v.labels["model"] == "T-800"

    merlin_active_model = merlin.active_model()
    all_versions = merlin_active_model.list_version(labels={"model": ["T-800"]})
    for version in all_versions:
        assert version.labels["model"] == "T-800"

    should_not_exist_versions = merlin_active_model.list_version(
        labels={"model": ["T-1000"]}
    )
    assert len(should_not_exist_versions) == 0


@pytest.mark.integration
@pytest.mark.dependency()
@pytest.mark.parametrize(
    "deployment_mode", [DeploymentMode.RAW_DEPLOYMENT, DeploymentMode.SERVERLESS]
)
def test_sklearn(
    integration_test_url, project_name, deployment_mode, use_google_oauth, requests
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model(
        f"sklearn-sample-{deployment_mode_suffix(deployment_mode)}", ModelType.SKLEARN
    )

    model_dir = "tests/caraml/models/sklearn-model"

    undeploy_all_version()

    with merlin.new_model_version() as v:
        merlin.log_model(model_dir=model_dir)

    endpoint = merlin.deploy(v, deployment_mode=deployment_mode)
    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(request_json["instances"])

    merlin.undeploy(v)


@pytest.mark.integration
@pytest.mark.dependency()
@pytest.mark.parametrize(
    "deployment_mode", [DeploymentMode.RAW_DEPLOYMENT, DeploymentMode.SERVERLESS]
)
def test_xgboost(
    integration_test_url, project_name, deployment_mode, use_google_oauth, requests
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model(
        f"xgboost-sample-{deployment_mode_suffix(deployment_mode)}", ModelType.XGBOOST
    )

    model_dir = "tests/caraml/models/xgboost-model"

    undeploy_all_version()

    with merlin.new_model_version() as v:
        # Upload the serialized model to MLP
        merlin.log_model(model_dir=model_dir)

    endpoint = merlin.deploy(v, deployment_mode=deployment_mode)
    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(request_json["instances"])

    merlin.undeploy(v)


@pytest.mark.integration
@pytest.mark.dependency()
@pytest.mark.parametrize(
    "deployment_mode", [DeploymentMode.RAW_DEPLOYMENT, DeploymentMode.SERVERLESS]
)
def test_model_schema(
    integration_test_url, project_name, deployment_mode, use_google_oauth, requests
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model(
        f"model-schema-{deployment_mode_suffix(deployment_mode)}", ModelType.XGBOOST
    )

    model_dir = "tests/caraml/models/xgboost-model"

    undeploy_all_version()
    model_schema = ModelSchema(
        spec=InferenceSchema(
            feature_types={
                "featureA": ValueType.FLOAT64,
                "featureB": ValueType.INT64,
                "featureC": ValueType.STRING,
                "featureD": ValueType.BOOLEAN,
            },
            prediction_id_column="prediction_id",
            model_prediction_output=BinaryClassificationOutput(
                prediction_score_column="score",
                actual_label_column="actual",
                positive_class_label="completed",
                negative_class_label="non_complete",
                score_threshold=0.7,
            ),
        )
    )

    with merlin.new_model_version(model_schema=model_schema) as v:
        # Upload the serialized model to MLP
        merlin.log_model(model_dir=model_dir)

    assert v.model_schema.spec == model_schema.spec

    endpoint = merlin.deploy(v, deployment_mode=deployment_mode)
    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(request_json["instances"])

    merlin.undeploy(v)


@pytest.mark.integration
def test_mlflow_tracking(
    integration_test_url, project_name, use_google_oauth, requests
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model("mlflow-test", ModelType.XGBOOST)

    model_dir = "tests/caraml/models/xgboost-model"

    undeploy_all_version()

    with merlin.new_model_version() as v:
        merlin.log_model(model_dir=model_dir)
        merlin.log_param("model_type", "xgboost")
        merlin.log_param("iteration", 5)

        merlin.set_tag("version", "v1.0")
        merlin.set_tag("build", "latest")
        merlin.set_tag("team_id", 1)

        merlin.log_metric("model_loaded", 10.23)

        assert merlin.get_param("model_type") == "xgboost"
        # Stringify value which is integer originally
        assert merlin.get_param("iteration") == "5"
        assert merlin.get_param("random_key") is None

        assert merlin.get_tag("version") == "v1.0"
        assert merlin.get_tag("xxx") is None
        # Stringify value which is integer originally
        assert merlin.get_tag("team_id") == "1"

        assert merlin.get_metric("model_loaded") == 10.23
        assert merlin.get_metric("response_time") is None

        assert merlin.list_tag() == {
            "version": "v1.0",
            "build": "latest",
            "team_id": "1",
        }

        # TODO: Support downloading artifacts from S3 or S3-compatible alternative (such as MinIO)
        # merlin.download_artifact("tests/caraml/models/downloaded_artifact")
        # artifact_dir = os.listdir('tests/caraml/models/downloaded_artifact')
        # assert len(artifact_dir) > 0  # not empty directory


@pytest.mark.integration
@pytest.mark.dependency()
@pytest.mark.parametrize(
    "deployment_mode", [DeploymentMode.RAW_DEPLOYMENT, DeploymentMode.SERVERLESS]
)
def test_tensorflow(
    integration_test_url, project_name, deployment_mode, use_google_oauth, requests
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model(
        f"tensorflow-sample-{deployment_mode_suffix(deployment_mode)}",
        ModelType.TENSORFLOW,
    )

    model_dir = "tests/caraml/models/tensorflow-model"

    undeploy_all_version()

    with merlin.new_model_version() as v:
        merlin.log_model(model_dir=model_dir)

    endpoint = merlin.deploy(v, deployment_mode=deployment_mode)
    resp = requests.post(f"{endpoint.url}", json=tensorflow_request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(tensorflow_request_json["instances"])

    merlin.undeploy(v)


@pytest.mark.pytorch
@pytest.mark.integration
@pytest.mark.dependency()
def test_pytorch(integration_test_url, project_name, use_google_oauth, requests):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model("pytorch-sample", ModelType.PYTORCH)

    model_dir = "tests/caraml/models/pytorch-model/pytorch-sample"

    undeploy_all_version()

    with merlin.new_model_version() as v:
        merlin.log_model(model_dir=model_dir)
        endpoint = merlin.deploy(v)

    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(request_json["instances"])

    merlin.undeploy(v)


@pytest.mark.serving
@pytest.mark.integration
def test_set_traffic(integration_test_url, project_name, use_google_oauth, requests):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model("set-traffic-sample", ModelType.SKLEARN)

    model_dir = "tests/caraml/models/sklearn-model"

    undeploy_all_version()

    with merlin.new_model_version() as v:
        # Upload the serialized model to MLP
        merlin.log_model(model_dir=model_dir)
        endpoint = merlin.deploy(v)

    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(request_json["instances"])

    endpoint = merlin.set_traffic({v: 100})
    sleep(3)

    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(request_json["instances"])

    # Try to undeploy serving model version. It must be fail
    with pytest.raises(Exception):
        assert merlin.undeploy(v)

    merlin.stop_serving_traffic(endpoint.environment_name)

    # Undeploy other running model version endpoints
    undeploy_all_version()


@pytest.mark.serving
@pytest.mark.integration
def test_serve_traffic(integration_test_url, project_name, use_google_oauth, requests):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model("serve-traffic-sample", ModelType.SKLEARN)

    model_dir = "tests/caraml/models/sklearn-model"

    undeploy_all_version()

    with merlin.new_model_version() as v:
        # Upload the serialized model to MLP
        merlin.log_model(model_dir=model_dir)
        endpoint = merlin.deploy(v)

    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(request_json["instances"])

    model_endpoint = merlin.serve_traffic({endpoint: 100})
    sleep(3)

    resp = requests.post(f"{model_endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(request_json["instances"])

    # Try to undeploy serving model version. It must be fail
    with pytest.raises(Exception):
        assert merlin.undeploy(v)

    merlin.stop_serving_traffic(model_endpoint.environment_name)

    # Undeploy other running model version endpoints
    undeploy_all_version()


@pytest.mark.integration
def test_multi_env(integration_test_url, project_name, use_google_oauth, requests):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model("multi-env", ModelType.XGBOOST)

    model_dir = "tests/caraml/models/xgboost-model"

    envs = merlin.list_environment()
    assert len(envs) >= 1

    default_env = merlin.get_default_environment()
    assert default_env is not None

    undeploy_all_version()

    with merlin.new_model_version() as v:
        # Upload the serialized model to MLP
        merlin.log_model(model_dir=model_dir)
        endpoint = merlin.deploy(v, environment_name=default_env.name)

    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(request_json["instances"])

    merlin.undeploy(v)


@pytest.mark.integration
@pytest.mark.parametrize(
    "deployment_mode", [DeploymentMode.RAW_DEPLOYMENT, DeploymentMode.SERVERLESS]
)
def test_resource_request(
    integration_test_url, project_name, deployment_mode, use_google_oauth, requests
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model(
        f"resource-request-{deployment_mode_suffix(deployment_mode)}", ModelType.XGBOOST
    )

    model_dir = "tests/caraml/models/xgboost-model"

    envs = merlin.list_environment()
    assert len(envs) >= 1

    default_env = merlin.get_default_environment()
    assert default_env is not None

    undeploy_all_version()
    with merlin.new_model_version() as v:
        # Upload the serialized model to MLP
        merlin.log_model(model_dir=model_dir)

        resource_request = ResourceRequest(1, 1, "100m", "256Mi")
        endpoint = merlin.deploy(
            v,
            environment_name=default_env.name,
            resource_request=resource_request,
            deployment_mode=deployment_mode,
        )

    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(request_json["instances"])

    merlin.undeploy(v)


@pytest.mark.gpu
@pytest.mark.integration
@pytest.mark.parametrize(
    "deployment_mode", [DeploymentMode.RAW_DEPLOYMENT, DeploymentMode.SERVERLESS]
)
def test_resource_request_with_gpu(
    integration_test_url,
    project_name,
    deployment_mode,
    use_google_oauth,
    requests,
    gpu_config,
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model(
        f"gpu-{deployment_mode_suffix(deployment_mode)}", ModelType.XGBOOST
    )

    model_dir = "tests/caraml/models/xgboost-model"

    envs = merlin.list_environment()
    assert len(envs) >= 1

    default_env = merlin.get_default_environment()
    assert default_env is not None

    undeploy_all_version()
    with merlin.new_model_version() as v:
        # Upload the serialized model to MLP
        merlin.log_model(model_dir=model_dir)

        resource_request = ResourceRequest(1, 1, "100m", "256Mi", **gpu_config)
        endpoint = merlin.deploy(
            v,
            environment_name=default_env.name,
            resource_request=resource_request,
            deployment_mode=deployment_mode,
        )

    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(request_json["instances"])

    merlin.undeploy(v)


# https://github.com/kserve/kserve/issues/2142
# Logging is not supported yet in raw_deployment
@pytest.mark.integration
@pytest.mark.parametrize(
    "deployment_mode", [DeploymentMode.RAW_DEPLOYMENT, DeploymentMode.SERVERLESS]
)
def test_logger(
    integration_test_url, project_name, deployment_mode, use_google_oauth, requests
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model(
        f"logger-{deployment_mode_suffix(deployment_mode)}", ModelType.TENSORFLOW
    )
    model_dir = "tests/caraml/models/tensorflow-model"

    undeploy_all_version()

    logger = Logger(model=LoggerConfig(enabled=True, mode=LoggerMode.ALL))
    with merlin.new_model_version() as v:
        merlin.log_model(model_dir=model_dir)
        endpoint = merlin.deploy(logger=logger, deployment_mode=deployment_mode)

    request_json = {
        "signature_name": "predict",
        "instances": [
            {
                "sepal_length": 2.8,
                "sepal_width": 1.0,
                "petal_length": 6.8,
                "petal_width": 0.4,
            },
            {
                "sepal_length": 0.1,
                "sepal_width": 0.5,
                "petal_length": 1.8,
                "petal_width": 2.4,
            },
        ],
    }
    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(tensorflow_request_json["instances"])

    merlin.undeploy(v)


@pytest.mark.customtransformer
@pytest.mark.integration
@pytest.mark.parametrize(
    "deployment_mode", [DeploymentMode.RAW_DEPLOYMENT, DeploymentMode.SERVERLESS]
)
def test_custom_transformer(
    integration_test_url, project_name, deployment_mode, use_google_oauth, requests
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model(
        f"custom-transformer-{deployment_mode_suffix(deployment_mode)}",
        ModelType.CUSTOM,
    )

    undeploy_all_version()

    transformer = Transformer(
        "gcr.io/kubeflow-ci/kfserving/image-transformer:latest",
    )

    logger = Logger(
        model=LoggerConfig(enabled=True, mode=LoggerMode.ALL),
        transformer=LoggerConfig(enabled=True, mode=LoggerMode.ALL),
    )

    with merlin.new_model_version() as v:
        v.log_custom_model(image="ealen/echo-server:0.5.1", args="--port 8080")
        endpoint = merlin.deploy(
            transformer=transformer, logger=logger, deployment_mode=deployment_mode
        )

    assert endpoint.logger is not None

    model_config = endpoint.logger.model
    assert model_config is not None
    assert model_config.enabled
    assert model_config.mode == LoggerMode.ALL

    transformer_config = endpoint.logger.transformer
    assert transformer_config is not None
    assert transformer_config.enabled
    assert transformer_config.mode == LoggerMode.ALL

    with open(os.path.join("tests/caraml/models/transformer", "input.json"), "r") as f:
        req = json.load(f)

    resp = requests.post(f"{endpoint.url}", json=req)

    assert resp.status_code == 200
    assert resp.json() is not None

    # Undeploy other running model version endpoints
    undeploy_all_version()


@pytest.mark.feast
@pytest.mark.integration
@pytest.mark.parametrize(
    "deployment_mode", [DeploymentMode.RAW_DEPLOYMENT, DeploymentMode.SERVERLESS]
)
def test_feast_enricher(
    integration_test_url, project_name, deployment_mode, use_google_oauth, requests
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model(
        f"feast-enricher-{deployment_mode_suffix(deployment_mode)}", ModelType.CUSTOM
    )

    undeploy_all_version()
    with merlin.new_model_version() as v:
        v.log_custom_model(image="ealen/echo-server:0.5.1", args="--port 8080")

    transformer_config_path = os.path.join(
        "tests/caraml/models/transformer", "feast_enricher.yaml"
    )
    transformer = StandardTransformer(config_file=transformer_config_path, enabled=True)

    request_json = {"driver_id": "1000"}
    endpoint = merlin.deploy(
        v, transformer=transformer, deployment_mode=deployment_mode
    )
    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    feast_features = resp.json()["request"]["body"]["feast_features"]
    assert feast_features is not None
    assert pd.DataFrame(feast_features) is not None

    merlin.undeploy(v)


@pytest.mark.integration
@pytest.mark.parametrize(
    "deployment_mode", [DeploymentMode.RAW_DEPLOYMENT, DeploymentMode.SERVERLESS]
)
def test_standard_transformer_without_feast(
    integration_test_url, project_name, deployment_mode, use_google_oauth, requests
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model(
        f"std-transformer-{deployment_mode_suffix(deployment_mode)}", ModelType.CUSTOM
    )

    undeploy_all_version()
    with merlin.new_model_version() as v:
        v.log_custom_model(image="ealen/echo-server:0.5.1", args="--port 8080")

    transformer_config_path = os.path.join(
        "tests/caraml/models/transformer", "standard_transformer_no_feast.yaml"
    )
    transformer = StandardTransformer(
        config_file=transformer_config_path,
        enabled=True,
        env_vars={"MODEL_TIMEOUT": "5s"},
    )

    endpoint = merlin.deploy(
        v, transformer=transformer, deployment_mode=deployment_mode
    )
    request_json = {
        "drivers": [
            # 1 Feb 2022, 00:00:00
            {
                "id": 1,
                "name": "driver-1",
                "vehicle": "motorcycle",
                "previous_vehicle": "suv",
                "rating": 4,
                "ep_time": 1643673600,
            },
            # 30 Jan 2022, 00:00:00
            {
                "id": 2,
                "name": "driver-2",
                "vehicle": "sedan",
                "previous_vehicle": "mpv",
                "rating": 3,
                "ep_time": 1643500800,
            },
        ],
        "customer": {"id": 1111},
    }
    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    exp_resp = {
        "instances": {
            "columns": [
                "customer_id",
                "name",
                "rank",
                "rating",
                "vehicle",
                "previous_vehicle",
                "ep_time_x",
                "ep_time_y",
            ],
            "data": [
                [1111, "driver-2", 2.5, 0.5, 2, 3, 1, 0],
                [1111, "driver-1", -2.5, 0.75, 0, 1, 1, 0],
            ],
        }
    }

    transformed_req = resp.json()["request"]["body"]
    recursive_eq(
        transformed_req["instances"], exp_resp["instances"], abs_tol=1e-09
    )  # asserts lhs = rhs, with tolerance
    merlin.undeploy(v)


@pytest.mark.feast
@pytest.mark.integration
@pytest.mark.parametrize(
    "deployment_mode", [DeploymentMode.RAW_DEPLOYMENT, DeploymentMode.SERVERLESS]
)
def test_standard_transformer_with_feast(
    integration_test_url, project_name, deployment_mode, use_google_oauth, requests
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model(
        f"std-transformer-feast-{deployment_mode_suffix(deployment_mode)}",
        ModelType.CUSTOM,
    )

    undeploy_all_version()
    with merlin.new_model_version() as v:
        v.log_custom_model(image="ealen/echo-server:0.5.1", args="--port 8080")

    transformer_config_path = os.path.join(
        "tests/caraml/models/transformer", "standard_transformer_with_feast.yaml"
    )
    transformer = StandardTransformer(config_file=transformer_config_path, enabled=True)

    endpoint = merlin.deploy(
        v, transformer=transformer, deployment_mode=deployment_mode
    )
    request_json = {
        "drivers": [
            {"id": "1234", "name": "driver-1"},
            {"id": "5678", "name": "driver-2"},
        ],
        "customer": {"id": 1111},
    }
    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    exp_resp = {
        "instances": {
            "columns": [
                "rank",
                "driver_id",
                "customer_id",
                "merlin_test_driver_features:test_int32",
                "merlin_test_driver_features:test_float",
            ],
            "data": [[0, "1234", 1111, -1, 0], [1, "5678", 1111, -1, 0]],
        }
    }

    assert resp.json()["request"]["body"]["instances"] == exp_resp["instances"]
    merlin.undeploy(v)


@pytest.mark.feast
@pytest.mark.integration
@pytest.mark.parametrize(
    "deployment_mode", [DeploymentMode.RAW_DEPLOYMENT, DeploymentMode.SERVERLESS]
)
def test_standard_transformer_with_multiple_feast(
    integration_test_url,
    project_name,
    deployment_mode,
    use_google_oauth,
    feast_serving_redis_url,
    feast_serving_bigtable_url,
    requests,
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model(
        f"std-transformer-feasts-{deployment_mode_suffix(deployment_mode)}",
        ModelType.CUSTOM,
    )

    undeploy_all_version()
    with merlin.new_model_version() as v:
        v.log_custom_model(image="ealen/echo-server:0.5.1", args="--port 8080")

    config_template_file_path = os.path.join(
        "tests/caraml/models/transformer",
        "standard_transformer_multiple_feast.yaml.tmpl",
    )
    config_file_path = os.path.join(
        "tests/caraml/models/transformer", "standard_transformer_multiple_feast.yaml"
    )

    from string import Template

    config_template_file = open(config_template_file_path, "rt")
    t = Template(config_template_file.read())
    rendered_config = t.substitute(
        {
            "feast_serving_redis_url": feast_serving_redis_url,
            "feast_serving_bigtable_url": feast_serving_bigtable_url,
        }
    )
    config_file = open(config_file_path, "wt")
    config_file.write(rendered_config)
    config_file.close()

    transformer = StandardTransformer(config_file=config_file_path, enabled=True)

    endpoint = merlin.deploy(
        v, transformer=transformer, deployment_mode=deployment_mode
    )
    request_json = {
        "drivers": [
            {"id": "driver_1", "name": "driver-1"},
            {"id": "driver_2", "name": "driver-2"},
        ],
        "customer": {"id": 1111},
    }
    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    exp_resp = {
        "instances": {
            "columns": [
                "rank",
                "driver_id",
                "customer_id",
                "merlin_test_redis_driver_features:completion_rate",
                "merlin_test_redis_driver_features:cancellation_rate",
                "merlin_test_bt_driver_features:rating",
            ],
            "data": [
                [0, "driver_1", 1111, 0.85, 0.15, 4.2],
                [1, "driver_2", 1111, 0.6, 0.4, 4.2],
            ],
        }
    }

    assert resp.json()["request"]["body"]["instances"] == exp_resp["instances"]
    merlin.undeploy(v)


@pytest.mark.skip(reason="Direct retrieval requires rework")
@pytest.mark.feast
@pytest.mark.integration
@pytest.mark.parametrize(
    "deployment_mode", [DeploymentMode.RAW_DEPLOYMENT, DeploymentMode.SERVERLESS]
)
def test_standard_transformer_with_multiple_feast_with_source(
    integration_test_url,
    project_name,
    deployment_mode,
    use_google_oauth,
    feast_serving_bigtable_url,
    requests,
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model(
        f"std-trf-feasts-source-{deployment_mode_suffix(deployment_mode)}",
        ModelType.CUSTOM,
    )

    undeploy_all_version()
    with merlin.new_model_version() as v:
        v.log_custom_model(image="ealen/echo-server:0.5.1", args="--port 8080")

    config_template_file_path = os.path.join(
        "tests/caraml/models/transformer",
        "standard_transformer_feast_with_source.yaml.tmpl",
    )
    config_file_path = os.path.join(
        "tests/caraml/models/transformer", "standard_transformer_multiple_feast.yaml"
    )

    from string import Template

    config_template_file = open(config_template_file_path, "rt")
    t = Template(config_template_file.read())
    rendered_config = t.substitute(
        {
            "feast_serving_bigtable_url": feast_serving_bigtable_url,
        }
    )
    config_file = open(config_file_path, "wt")
    config_file.write(rendered_config)
    config_file.close()

    env_vars = {
        "FEAST_REDIS_DIRECT_STORAGE_ENABLED": True,
        "FEAST_REDIS_POOL_SIZE": 1,
        "FEAST_BIGTABLE_DIRECT_STORAGE_ENABLED": True,
        "FEAST_BIGTABLE_POOL_SIZE": 1,
        "FEAST_BIGTABLE_KEEP_ALIVE_INTERVAL": "2m",
        "FEAST_BIGTABLE_KEEP_ALIVE_TIMEOUT": "15s",
    }
    transformer = StandardTransformer(
        config_file=config_file_path, enabled=True, env_vars=env_vars
    )

    endpoint = merlin.deploy(
        v, transformer=transformer, deployment_mode=deployment_mode
    )
    request_json = {
        "drivers": [
            {"id": "driver_1", "name": "driver-1"},
            {"id": "driver_2", "name": "driver-2"},
        ],
        "customer": {"id": 1111},
    }
    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    exp_resp = {
        "instances": {
            "columns": [
                "rank",
                "driver_id",
                "customer_id",
                "merlin_test_redis_driver_features:completion_rate",
                "merlin_test_redis_driver_features:cancellation_rate",
                "merlin_test_bt_driver_features:rating",
            ],
            "data": [
                [0, "driver_1", 1111, 0.85, 0.15, 4.2],
                [1, "driver_2", 1111, 0.6, 0.4, 4.2],
            ],
        }
    }

    assert resp.json()["request"]["body"]["instances"] == exp_resp["instances"]
    merlin.undeploy(v)


@pytest.mark.integration
def test_custom_model_without_artifact(
    integration_test_url, project_name, use_google_oauth, requests
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model("custom-wo-artifact", ModelType.CUSTOM)

    undeploy_all_version()

    with merlin.new_model_version() as v:
        v.log_custom_model(image="ealen/echo-server:0.5.1", args="--port 8080")

    endpoint = merlin.deploy(v)

    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    # Undeploy other running model version endpoints
    undeploy_all_version()


@pytest.mark.integration
@pytest.mark.parametrize(
    "deployment_mode", [DeploymentMode.RAW_DEPLOYMENT, DeploymentMode.SERVERLESS]
)
def test_custom_model_with_artifact(
    integration_test_url, project_name, deployment_mode, use_google_oauth, requests
):
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model(
        f"custom-w-artifact-{deployment_mode_suffix(deployment_mode)}", ModelType.CUSTOM
    )
    undeploy_all_version()

    model_dir = "tests/caraml/models/custom-model"
    BST_FILE = "model.bst"

    with merlin.new_model_version() as v:
        v.log_custom_model(
            image="ghcr.io/tiopramayudi/custom-predictor-go:v0.2", model_dir=model_dir
        )

    endpoint = merlin.deploy(
        v,
        env_vars={"MODEL_FILE_NAME": BST_FILE},
        deployment_mode=deployment_mode,
    )

    resp = requests.post(f"{endpoint.url}", json=request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert resp.json()["predictions"] is not None
    # Undeploy other running model version endpoints
    undeploy_all_version()


@pytest.mark.raw_deployment
@pytest.mark.integration
def test_deployment_mode_for_serving_model(
    integration_test_url, project_name, use_google_oauth, requests
):
    """
    Validate that set traffic is working when switching from different deployment mode
    """
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model("serve-raw-deployment", ModelType.TENSORFLOW)
    model_dir = "tests/caraml/models/tensorflow-model"

    undeploy_all_version()

    # Upload new model version: v1
    with merlin.new_model_version() as v1:
        merlin.log_model(model_dir=model_dir)

    # Deploy using serverless with RPS autoscaling policy
    endpoint = merlin.deploy(
        v1,
        autoscaling_policy=merlin.AutoscalingPolicy(
            metrics_type=merlin.MetricsType.RPS, target_value=20
        ),
    )

    resp = requests.post(f"{endpoint.url}", json=tensorflow_request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(tensorflow_request_json["instances"])

    # Set v1 as serving model
    initial_model_endpoint = merlin.set_traffic({v1: 100})
    resp = requests.post(f"{initial_model_endpoint.url}", json=tensorflow_request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(tensorflow_request_json["instances"])

    # Test that user can't change deployment mode of a serving model
    with pytest.raises(Exception):
        endpoint = merlin.deploy(v1, deployment_mode=DeploymentMode.RAW_DEPLOYMENT)

    # Upload new model version: v2
    with merlin.new_model_version() as v2:
        merlin.log_model(model_dir=model_dir)

    # Deploy v2 using raw_deployment with CPU autoscaling policy
    new_endpoint = merlin.deploy(
        v2,
        deployment_mode=DeploymentMode.RAW_DEPLOYMENT,
        autoscaling_policy=merlin.AutoscalingPolicy(
            metrics_type=merlin.MetricsType.CPU_UTILIZATION, target_value=20
        ),
    )

    resp = requests.post(f"{new_endpoint.url}", json=tensorflow_request_json)

    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(tensorflow_request_json["instances"])

    # Set v2 as serving model
    model_endpoint = merlin.set_traffic({v2: 100})
    assert model_endpoint.url == initial_model_endpoint.url

    resp = requests.post(f"{model_endpoint.url}", json=tensorflow_request_json)
    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(tensorflow_request_json["instances"])

    # Set v1 back as serving model
    model_endpoint = merlin.set_traffic({v1: 100})
    assert model_endpoint.url == initial_model_endpoint.url

    resp = requests.post(f"{model_endpoint.url}", json=tensorflow_request_json)
    assert resp.status_code == 200
    assert resp.json() is not None
    assert len(resp.json()["predictions"]) == len(tensorflow_request_json["instances"])

    merlin.stop_serving_traffic(model_endpoint.environment_name)
    undeploy_all_version()


@pytest.mark.integration
def test_redeploy_model(integration_test_url, project_name, use_google_oauth, requests):
    """
    Validate that calling the 'merlin.deploy' twice in a row redeploys a Merlin model
    """

    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)
    merlin.set_project(project_name)
    merlin.set_model("model-sdk-redeploy", ModelType.CUSTOM)

    undeploy_all_version()

    # Upload new model version: v1
    with merlin.new_model_version() as v1:
        v1.log_custom_model(image="ealen/echo-server:0.5.1", args="--port 8080")

    # Deploy using raw_deployment with CPU autoscaling policy
    endpoint = merlin.deploy(
        v1,
        resource_request=merlin.ResourceRequest(1, 1, "123m", "234Mi"),
        env_vars={"green": "TRUE"},
        autoscaling_policy=merlin.AutoscalingPolicy(
            metrics_type=merlin.MetricsType.CPU_UTILIZATION, target_value=50
        ),
        deployment_mode=DeploymentMode.RAW_DEPLOYMENT,
        transformer=Transformer(
            image="gcr.io/kubeflow-ci/kfserving/image-transformer:latest"
        ),
    )

    with open(os.path.join("tests/caraml/models/transformer", "input.json"), "r") as f:
        req = json.load(f)

    resp = requests.post(f"{endpoint.url}", json=req)
    assert resp.status_code == 200
    assert resp.json() is not None

    # Check the deployment configs of v1
    assert endpoint.resource_request.cpu_request == "123m"
    assert endpoint.resource_request.memory_request == "234Mi"
    assert endpoint.env_vars == {"green": "TRUE"}
    assert endpoint.deployment_mode == DeploymentMode.RAW_DEPLOYMENT

    # Check the autoscaling policy of v1
    assert endpoint.autoscaling_policy.metrics_type == MetricsType.CPU_UTILIZATION
    assert endpoint.autoscaling_policy.target_value == 50

    # Check that the transformer id is set
    assert endpoint.transformer.id != ""

    sleep(10)

    # Deploy v2 using raw_deployment with CPU autoscaling policy; update transformer specs.
    new_endpoint = merlin.deploy(
        v1,
        autoscaling_policy=merlin.AutoscalingPolicy(
            metrics_type=merlin.MetricsType.CPU_UTILIZATION, target_value=90
        ),
        deployment_mode=DeploymentMode.RAW_DEPLOYMENT,
        transformer=Transformer(
            image="gcr.io/kubeflow-ci/kfserving/image-transformer:latest",
            resource_request=merlin.ResourceRequest(0, 1, "100m", "250Mi"),
        ),
    )

    resp = requests.post(f"{new_endpoint.url}", json=req)
    assert resp.status_code == 200
    assert resp.json() is not None

    # Check that the endpoint remains the same
    assert endpoint.url == new_endpoint.url

    # Check that the deployment configs of v2 have remained the same as those used in v1
    assert endpoint.resource_request.cpu_request == "123m"
    assert endpoint.resource_request.memory_request == "234Mi"
    assert endpoint.env_vars == {"green": "TRUE"}
    assert endpoint.deployment_mode == DeploymentMode.RAW_DEPLOYMENT

    # Check the autoscaling policy of v2
    assert new_endpoint.autoscaling_policy.metrics_type == MetricsType.CPU_UTILIZATION
    assert new_endpoint.autoscaling_policy.target_value == 90

    # Check that the transformer id remains the same
    assert endpoint.transformer.id == new_endpoint.transformer.id

    undeploy_all_version()


def deployment_mode_suffix(deployment_mode: DeploymentMode):
    return deployment_mode.value.lower()[0:1]


@pytest.mark.integration
def test_standard_transformer_simulate(integration_test_url, use_google_oauth):
    """
    Test the `simulate` method of the `StandardTransformer` class.
    """
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)

    transformer_config_path = os.path.join(
        "tests/caraml/models/transformer", "standard_transformer_no_feast.yaml"
    )
    transformer = StandardTransformer(
        config_file=transformer_config_path, enabled=False
    )

    payload = {
        "drivers": [
            # 1 Feb 2022, 00:00:00
            {
                "id": 1,
                "name": "driver-1",
                "vehicle": "motorcycle",
                "previous_vehicle": "suv",
                "rating": 4,
                "ep_time": 1643673600,
            },
            # 30 Jan 2022, 00:00:00
            {
                "id": 2,
                "name": "driver-2",
                "vehicle": "sedan",
                "previous_vehicle": "mpv",
                "rating": 3,
                "ep_time": 1643500800,
            },
        ],
        "customer": {"id": 1111},
    }

    resp_wo_tracing = transformer.simulate(payload=payload, exclude_tracing=True)
    resp_w_tracing = transformer.simulate(payload=payload, exclude_tracing=False)

    def remove_nulls(d):
        return {k: v for k, v in d.items() if v is not None}

    with open(
        "tests/caraml/models/transformer/sim_exp_resp_valid_wo_tracing.json", "r"
    ) as f:
        exp_resp_valid_wo_tracing = json.load(f, object_hook=remove_nulls)

    with open(
        "tests/caraml/models/transformer/sim_exp_resp_valid_w_tracing.json", "r"
    ) as f:
        exp_resp_valid_w_tracing = json.load(f, object_hook=remove_nulls)

    assert isinstance(resp_wo_tracing, dict)
    assert isinstance(resp_w_tracing, dict)
    assert "response" in resp_wo_tracing.keys()
    assert "response" in resp_w_tracing.keys()
    assert "operation_tracing" not in resp_wo_tracing.keys()
    assert "operation_tracing" in resp_w_tracing.keys()
    assert resp_wo_tracing == exp_resp_valid_wo_tracing
    assert resp_w_tracing == exp_resp_valid_w_tracing


@pytest.mark.feast
@pytest.mark.integration
def test_standard_transformer_simulate_feast(integration_test_url, use_google_oauth):
    """
    Test the `simulate` method of the `StandardTransformer` class with Feast enricher.
    """
    merlin.set_url(integration_test_url, use_google_oauth=use_google_oauth)

    transformer_config_path = os.path.join(
        "tests/caraml/models/transformer", "standard_transformer_with_feast.yaml"
    )
    transformer = StandardTransformer(config_file=transformer_config_path, enabled=True)

    request_json = {
        "drivers": [
            {"id": "1234", "name": "driver-1"},
            {"id": "5678", "name": "driver-2"},
        ],
        "customer": {"id": 1111},
    }

    response_w_tracing = transformer.simulate(
        payload=request_json, exclude_tracing=True
    )
    response_wo_tracing = transformer.simulate(
        payload=request_json, exclude_tracing=False
    )

    with open(
        "tests/caraml/models/transformer/sim_exp_resp_feast_w_tracing.json", "r"
    ) as f:
        exp_resp_w_tracing = json.load(f)

    with open(
        "tests/caraml/models/transformer/sim_exp_resp_feast_wo_tracing.json", "r"
    ) as f:
        exp_resp_wo_tracing = json.load(f)

    assert isinstance(response_w_tracing, dict)
    assert isinstance(response_wo_tracing, dict)
    assert "response" in response_w_tracing.keys()
    assert "response" in response_wo_tracing.keys()
    assert "operation_tracing" not in response_wo_tracing.keys()
    assert "operation_tracing" in response_w_tracing.keys()
    assert response_w_tracing == exp_resp_w_tracing
    assert response_wo_tracing == exp_resp_wo_tracing
