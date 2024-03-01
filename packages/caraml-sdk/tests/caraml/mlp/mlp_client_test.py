
import datetime
import pytest

from mlp.mlp_client import MLPClient
from mlp.client.models import Project

# get global mock responses that configured in conftest
responses = pytest.responses


created_at = "2019-08-29T08:13:12.377Z"
updated_at = "2019-08-29T08:13:12.377Z"


@responses.activate
def test_get_project(mock_url, mock_oauth, use_google_oauth):
    responses.add(
        "GET",
        "/v1/projects",
        body=f"""[{{
                        "id": 0,
                        "name": "my-project",
                        "mlflow_tracking_url": "http://mlflow.api.dev",
                        "created_at": "{created_at}",
                        "updated_at": "{updated_at}"
                      }}]""",
        status=200,
        content_type="application/json",
    )

    m = MLPClient(mock_url, use_google_oauth=use_google_oauth)
    p = m.get_project("my-project")

    assert responses.calls[-1].request.method == "GET"
    assert responses.calls[-1].request.url == "/v1/projects?name=my-project"
    assert responses.calls[-1].request.host == "127.0.0.1"

    assert p.id == 0
    assert p.name == "my-project"
    assert p.mlflow_tracking_url == "http://mlflow.api.dev"
    assert isinstance(p.created_at, datetime.datetime)
    assert isinstance(p.updated_at, datetime.datetime)


@responses.activate
def test_get_invalid_project_name(
    mock_url, api_client, mock_oauth, use_google_oauth
):
    project_name = "invalidProjectName"

    client = MLPClient(mock_url, use_google_oauth=use_google_oauth)

    # Try to create project with invalid name. It must be fail
    with pytest.raises(Exception):
        assert client.get_project(project_name)

@responses.activate
def test_list_projects(mock_url, mock_oauth, use_google_oauth):
    projects = [
        Project.from_dict({
                        "id": 0,
                        "name": "my-project",
                        "mlflow_tracking_url": "http://mlflow.api.dev",
                        "created_at": created_at,
                        "updated_at": updated_at
                      }),
        Project.from_dict({
                        "id": 1,
                        "name": "my-project-1",
                        "mlflow_tracking_url": "http://mlflow.api.dev",
                        "created_at": created_at,
                        "updated_at": updated_at
                      })
    ]
    responses.add(
        method="GET",
        url=f"/v1/projects",
        body=f"""[{{
                        "id": 0,
                        "name": "my-project",
                        "mlflow_tracking_url": "http://mlflow.api.dev",
                        "created_at": "{created_at}",
                        "updated_at": "{updated_at}"
                      }},
                    {{
                        "id": 1,
                        "name": "my-project-1",
                        "mlflow_tracking_url": "http://mlflow.api.dev",
                        "created_at": "{created_at}",
                        "updated_at": "{updated_at}"
                      }}]""",
        status=200,
        content_type="application/json",
    )

    m = MLPClient(mock_url, use_google_oauth=use_google_oauth)
    actual = m.list_projects()

    assert len(actual) == len(projects)
    assert all([isinstance(p, Project) for p in actual])

    for actual, expected in zip(actual, projects):
        assert actual.id == expected.id
        assert actual.name == expected.name
        assert actual.mlflow_tracking_url == expected.mlflow_tracking_url
        assert actual.created_at == expected.created_at
        assert actual.updated_at == expected.updated_at

    m.list_projects(name="project_1")
    assert responses.calls[-1].request.url == "/v1/projects?name=project_1"
