from dataclasses import dataclass, field
from typing import Dict

import routers.client.models
from routers.client.model_utils import OpenApiModel


@dataclass
class ExperimentConfig:
    type: str = "nop"
    config: Dict = None

    def __init__(self, type: str = "nop", config: Dict = None, **kwargs):
        self.type = type
        self.config = config
        self.__dict__.update(kwargs)

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, type: str):
        self._type = type

    @property
    def config(self) -> Dict:
        return self._config

    @config.setter
    def config(self, config: Dict):
        self._config = config
        if self._config is not None and "project_id" in self._config:
            self.config["project_id"] = int(self._config["project_id"])

    def to_open_api(self) -> OpenApiModel:
        if self.config is None:
            config = {}
        else:
            config = self.config

        return routers.client.models.ExperimentConfig(type=self.type, config=config)
