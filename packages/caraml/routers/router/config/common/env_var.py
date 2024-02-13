from dataclasses import dataclass, field

import routers.client.models
from routers.client.model_utils import OpenApiModel


@dataclass
class EnvVar:
    name: str
    value: str

    _name: str = field(init=False, repr=False)
    _value: str = field(init=False, repr=False)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value

    def to_open_api(self) -> OpenApiModel:
        return routers.client.models.EnvVar(name=self.name, value=self.value)
