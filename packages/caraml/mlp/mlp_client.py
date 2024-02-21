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
from sys import version_info
from typing import List

import urllib3
from caraml_auth.id_token_credentials import get_default_id_token_credentials

from mlp.client import (
    ApiClient,
    Configuration,
    ProjectApi,
    SecretApi,
    Project
    
)
from mlp.version import VERSION

from google.auth.transport.requests import Request
from google.auth.transport.urllib3 import AuthorizedHttp

from models.util import valid_name_check


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
        self._project_api = ProjectApi(self._api_client)
        self._secret_api = SecretApi(self._api_client)

    @property
    def url(self):
        return self._merlin_url


    def list_project(self) -> List[Project]:
        """
        List project in the connected MLP server

        :return: list of Project
        """
        p_list = self._project_api.projects_get()
        result = []
        for p in p_list:
            result.append(Project(p, self.url, self._api_client))
        return result

    def get_or_create_project(self, project_name: str) -> Project:
        warnings.warn(
            "get_or_create_project is deprecated please use get_project",
            category=DeprecationWarning,
        )
        return self.get_project(project_name)

    def get_project(self, project_name: str) -> Project:
        """
        Get a project in Merlin and optionally assign list of readers and administrators.
        The identity used for creating the project will be automatically included as project's administrators.

        :param project_name: project name
        :return: project
        """
        if not valid_name_check(project_name):
            raise ValueError(
                """Your project/model name contains invalid characters.\
                    \nUse only the following characters\
                    \n- Characters: a-z (Lowercase ONLY)\
                    \n- Numbers: 0-9\
                    \n- Symbols: -
                """
            )

        p_list = self._project_api.projects_get(name=project_name)
        p = None
        for prj in p_list:
            if prj.name == project_name:
                p = prj

        if p is None:
            raise Exception(
                f"{project_name} does not exist or you don't have access to the project. Please create new "
                f"project using MLP console or ask the project's administrator to be able to access "
                f"existing project."
            )

        return Project(p, self.url, self._api_client)
