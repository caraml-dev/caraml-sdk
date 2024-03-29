import json
import pytest
from urllib3_mock import Responses

import routers as turing
import routers.client.models
from routers.router.config.router_version import RouterVersion

from tests.routers import utils

responses = Responses("requests.packages.urllib3")


@pytest.fixture(scope="module", name="responses")
def _responses():
    return responses


@responses.activate
def test_create_version(
    turing_api,
    active_project,
    generic_router_config,
    generic_router_version,
    use_google_oauth,
):
    turing.set_url(turing_api, use_google_oauth)
    turing.set_project(active_project.name)

    test_router_id = 1

    responses.add(
        method="POST",
        url=f"/v1/projects/{active_project.id}/routers/{test_router_id}/versions",
        body=json.dumps(generic_router_version, default=utils.json_serializer),
        status=200,
        content_type="application/json",
    )

    actual_response = RouterVersion.create(generic_router_config, test_router_id)

    assert actual_response.id == generic_router_version.id
    assert actual_response.monitoring_url == generic_router_version.monitoring_url
    assert actual_response.status.value == generic_router_version.status.value
    assert actual_response.created_at == generic_router_version.created_at
    assert actual_response.updated_at == generic_router_version.updated_at

    assert len(actual_response.rules) == len(generic_router_version.rules)
    for i in range((len(actual_response.rules))):
        assert actual_response.rules[i].to_open_api() == generic_router_version.rules[i]

    assert actual_response.default_route_id == generic_router_version.default_route_id
    assert (
        actual_response.experiment_engine.to_open_api()
        == generic_router_version.experiment_engine
    )
    assert (
        actual_response.resource_request.to_open_api()
        == generic_router_version.resource_request
    )
    assert actual_response.timeout == generic_router_version.timeout

    assert (
        actual_response.log_config.to_open_api().result_logger_type
        == generic_router_version.log_config.result_logger_type
    )

    assert actual_response.enricher.image == generic_router_version.enricher.image
    assert (
        actual_response.enricher.resource_request.to_open_api()
        == generic_router_version.enricher.resource_request
    )
    assert actual_response.enricher.endpoint == generic_router_version.enricher.endpoint
    assert actual_response.enricher.timeout == generic_router_version.enricher.timeout
    assert actual_response.enricher.port == generic_router_version.enricher.port

    assert actual_response.ensembler.type == generic_router_version.ensembler.type
