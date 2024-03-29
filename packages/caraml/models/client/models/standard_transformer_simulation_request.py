# coding: utf-8

"""
    Merlin

    API Guide for accessing Merlin's model management, deployment, and serving functionalities

    The version of the OpenAPI document: 0.14.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json


from typing import Any, ClassVar, Dict, List, Optional, Union
from pydantic import BaseModel
from models.client.models.model_prediction_config import ModelPredictionConfig
from models.client.models.protocol import Protocol

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self


class StandardTransformerSimulationRequest(BaseModel):
    """
    StandardTransformerSimulationRequest
    """  # noqa: E501

    payload: Optional[Union[str, Any]] = None
    headers: Optional[Union[str, Any]] = None
    config: Optional[Union[str, Any]] = None
    model_prediction_config: Optional[ModelPredictionConfig] = None
    protocol: Optional[Protocol] = None
    __properties: ClassVar[List[str]] = [
        "payload",
        "headers",
        "config",
        "model_prediction_config",
        "protocol",
    ]

    model_config = {"populate_by_name": True, "validate_assignment": True}

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of StandardTransformerSimulationRequest from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        _dict = self.model_dump(
            by_alias=True,
            exclude={},
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of model_prediction_config
        if self.model_prediction_config:
            _dict["model_prediction_config"] = self.model_prediction_config.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Dict) -> Self:
        """Create an instance of StandardTransformerSimulationRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "payload": obj.get("payload"),
                "headers": obj.get("headers"),
                "config": obj.get("config"),
                "model_prediction_config": ModelPredictionConfig.from_dict(
                    obj.get("model_prediction_config")
                )
                if obj.get("model_prediction_config") is not None
                else None,
                "protocol": obj.get("protocol"),
            }
        )
        return _obj
