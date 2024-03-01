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

import warnings
import urllib3
import mlflow

from sys import version_info
from typing import List, Optional
from mlp.client import (
    ApiClient,
    Configuration,
    ProjectApi,
    SecretApi,
    Project
    
)
from mlp.version import VERSION
from caraml_auth.id_token_credentials import get_default_id_token_credentials
from google.auth.transport.requests import Request
from google.auth.transport.urllib3 import AuthorizedHttp

from common.utils import is_valid_project_name


def require_active_project(f):
    def wrap(*args, **kwargs):
        if not args[0].active_project:
            raise Exception("Active project isn't set, use set_project(...) to set it")
        return f(*args, **kwargs)

    return wrap

class MLPClient:
    def __init__(self, mlp_url: str, use_google_oauth: bool = True, caraml_sdk_version: str = ""):
        self._mlp_url = mlp_url
        config = Configuration()
        config.host = self._mlp_url

        self._api_client = ApiClient(config)
        if use_google_oauth:
            credentials = get_default_id_token_credentials(target_audience="sdk.caraml")
            # Refresh credentials, in case it's coming from Compute Engine.
            # See: https://github.com/googleapis/google-auth-library-python/issues/1211
            credentials.refresh(Request())
            authorized_http = AuthorizedHttp(credentials, urllib3.PoolManager()) # TODO: Create a common pool manager with retries. 
            self._api_client.rest_client.pool_manager = authorized_http

        python_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"  # capture user's python version
        user_agent = f"mlp-sdk/{VERSION} python/{python_version}"
        if caraml_sdk_version:
            user_agent = f"caraml-sdk/{caraml_sdk_version} " + user_agent
        self._api_client.user_agent = user_agent
        
        self._project = None
        self._project_api = ProjectApi(self._api_client)
        self._secret_api = SecretApi(self._api_client)

    @property
    def url(self):
        return self._mlp_url
    
    @property
    def active_project(self) -> Optional[Project]:
        return self._project

    @active_project.setter
    def active_project(self, project):
        mlflow.tracking.set_tracking_uri(project.mlflow_tracking_url)
        self._project = project

    def set_project(self, project_name: str):
        """
        Set this session's active projects
        """
        self.active_project = self.get_project(project_name)


    def list_projects(self, name: Optional[str] = None) -> List[Project]:
        """
        List all projects, that the current user has access to

        :param name: filter projects by name
        :return: list of projects
        """
        kwargs = {}
        if name:
            kwargs["name"] = name
        return self._project_api.v1_projects_get(**kwargs)


    def get_project(self, project_name: str) -> Project:
        """
        Get a project from CaraML.
        The identity used for creating the project will be automatically included as project's administrators.

        :param project_name: project name
        :return: project
        """
        if not is_valid_project_name(project_name):
            raise ValueError(
                """Your project/model name contains invalid characters.\
                    \nUse only the following characters\
                    \n- Characters: a-z (Lowercase ONLY)\
                    \n- Numbers: 0-9\
                    \n- Symbols: -
                """
            )

        projects = self.list_projects(name=project_name)

        filtered = [p for p in projects if p.name == project_name][:1]
        if not filtered:
            raise Exception(
                f"{project_name} does not exist or you don't have access to the project. Please create new "
                f"project using MLP console or ask the project's administrator to be able to access "
                f"existing project."
            )

        return filtered[0]
