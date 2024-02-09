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

from enum import Enum
from typing import Dict

import models.client as client
from models.autoscaling import (RAW_DEPLOYMENT_DEFAULT_AUTOSCALING_POLICY,
                                SERVERLESS_DEFAULT_AUTOSCALING_POLICY,
                                AutoscalingPolicy, MetricsType)
from models.deployment_mode import DeploymentMode
from models.environment import Environment
from models.logger import Logger
from models.protocol import Protocol
from models.util import autostr, get_url
from models.resource_request import ResourceRequest
from models.transformer import Transformer


class Status(Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    SERVING = 'serving'
    FAILED = 'failed'
    TERMINATED = 'terminated'


@autostr
class VersionEndpoint:
    def __init__(self, endpoint: client.VersionEndpoint, log_url: str = None):
        self._protocol = Protocol.HTTP_JSON
        if endpoint.protocol:
            self._protocol = Protocol(endpoint.protocol)

        self._url = endpoint.url
        if self._protocol == Protocol.HTTP_JSON and ":predict" not in endpoint.url:
            self._url = f"{endpoint.url}:predict"

        self._status = Status(endpoint.status)
        self._id = endpoint.id
        self._environment_name = endpoint.environment_name
        self._environment = Environment(endpoint.environment)
        self._env_vars = endpoint.env_vars
        self._logger = Logger.from_logger_response(endpoint.logger)
        self._resource_request = endpoint.resource_request
        self._deployment_mode = DeploymentMode.SERVERLESS if not endpoint.deployment_mode \
            else DeploymentMode(endpoint.deployment_mode)

        if endpoint.autoscaling_policy is None:
            if self._deployment_mode == DeploymentMode.SERVERLESS:
                self._autoscaling_policy = SERVERLESS_DEFAULT_AUTOSCALING_POLICY
            else:
                self._autoscaling_policy = RAW_DEPLOYMENT_DEFAULT_AUTOSCALING_POLICY
        else:
            self._autoscaling_policy = AutoscalingPolicy(metrics_type=MetricsType(endpoint.autoscaling_policy.metrics_type),
                                                         target_value=endpoint.autoscaling_policy.target_value)

        if endpoint.transformer is not None:
            self._transformer = Transformer(
                endpoint.transformer.image, id=endpoint.transformer.id,
                enabled=endpoint.transformer.enabled, command=endpoint.transformer.command,
                args=endpoint.transformer.args, transformer_type=endpoint.transformer.transformer_type,
                resource_request=endpoint.transformer.resource_request, env_vars=endpoint.transformer.env_vars,
            )
            
        if log_url is not None:
            self._log_url = log_url

        self._enable_model_observability = endpoint.enable_model_observability

    @property
    def url(self):
        return self._url

    @property
    def status(self) -> Status:
        return self._status

    @property
    def id(self) -> str:
        return self._id

    @property
    def environment_name(self) -> str:
        return self._environment_name

    @property
    def environment(self) -> Environment:
        return self._environment

    @property
    def env_vars(self) -> Dict[str, str]:
        env_vars = {}
        if self._env_vars:
            for ev in self._env_vars:
                env_vars[ev.name] = ev.value
        return env_vars

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def log_url(self) -> str:
        return self._log_url

    @property
    def deployment_mode(self) -> DeploymentMode:
        return self._deployment_mode

    @property
    def autoscaling_policy(self) -> AutoscalingPolicy:
        return self._autoscaling_policy

    @property
    def protocol(self) -> Protocol:
        return self._protocol
    
    @property
    def resource_request(self) -> ResourceRequest:
        return self._resource_request
    
    @property
    def transformer(self) -> Transformer:
        return self._transformer
    
    @property
    def enable_model_observability(self) -> bool:
        return self._enable_model_observability

    def _repr_html_(self):
        return f"""<a href="{self._url}">{self._url}</a>"""


@autostr
class ModelEndpoint:
    def __init__(self, endpoint: client.ModelEndpoint):
        self._protocol = Protocol.HTTP_JSON
        if endpoint.protocol:
            self._protocol = Protocol(endpoint.protocol)

        if self._protocol == Protocol.HTTP_JSON:
            self._url = get_url(f"{endpoint.url}/v1/predict")
        else:
            self._url = endpoint.url
        self._status = Status(endpoint.status)
        self._id = endpoint.id
        self._environment_name = endpoint.environment_name
        self._environment = Environment(endpoint.environment)


    @property
    def url(self):
        return self._url

    @property
    def status(self) -> Status:
        return self._status

    @property
    def id(self) -> str:
        return str(self._id)

    @property
    def environment_name(self) -> str:
        return self._environment_name

    @property
    def environment(self) -> Environment:
        return self._environment

    @property
    def protocol(self) -> Protocol:
        return self._protocol

    def _repr_html_(self):
        return f"""<a href="{self._url}">{self._url}</a>"""