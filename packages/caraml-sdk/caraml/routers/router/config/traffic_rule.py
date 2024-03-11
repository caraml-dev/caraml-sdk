import abc
import dataclasses
from enum import Enum
from collections import Counter
from dataclasses import dataclass
from typing import List, Union, Dict

import caraml.routers.client.models
from caraml.routers.router.config.route import Route
from caraml.routers.client.model_utils import OpenApiModel


class FieldSource(Enum):
    HEADER = "header"
    PAYLOAD = "payload"
    PREDICTION_CONTEXT = "prediction_context"

    def to_open_api(self) -> OpenApiModel:
        return caraml.routers.client.models.FieldSource(self.value)


@dataclass
class TrafficRuleCondition:
    """
    Class to create a new TrafficRuleCondition

    :param field_source: the source of the field specified
    :param field: name of the field specified
    :param operator: name of the operator (fixed as 'in')
    :param values: values that are supposed to match those found in the field
    """

    field_source: FieldSource
    field: str
    operator: str
    values: List[str]

    _field_source: FieldSource = dataclasses.field(init=False, repr=False)
    _field: str = dataclasses.field(init=False, repr=False)
    _operator: str = dataclasses.field(init=False, repr=False)
    _values: List[str] = dataclasses.field(init=False, repr=False)

    @property
    def field_source(self) -> FieldSource:
        return self._field_source

    @field_source.setter
    def field_source(self, field_source: Union[FieldSource, str]):
        if isinstance(field_source, FieldSource):
            self._field_source = field_source
        elif isinstance(field_source, str):
            self._field_source = FieldSource(field_source)
        else:
            self._field_source = field_source

    @property
    def field(self) -> str:
        return self._field

    @field.setter
    def field(self, field: str):
        self._field = field

    @property
    def operator(self) -> str:
        return self._operator

    @operator.setter
    def operator(self, operator: str):
        TrafficRuleCondition._verify_operator(operator)
        self._operator = operator

    @property
    def values(self) -> List[str]:
        return self._values

    @values.setter
    def values(self, values: List[str]):
        self._values = values

    def to_open_api(self) -> OpenApiModel:
        return caraml.routers.client.models.TrafficRuleCondition(
            field_source=self.field_source.to_open_api(),
            field=self.field,
            operator=self.operator,
            values=self.values,
        )

    @classmethod
    def _verify_operator(cls, operator):
        if operator != "in":
            raise InvalidOperatorException(f"Invalid operator passed: {operator}")


class InvalidOperatorException(Exception):
    pass


@dataclass
class HeaderTrafficRuleCondition(TrafficRuleCondition):
    def __init__(self, field: str, values: List[str]):
        """
        Method to create a new TrafficRuleCondition that is defined on a request header

        :param field: name of the field specified
        :param values: values that are supposed to match those found in the field
        """
        super().__init__(
            field_source=FieldSource.HEADER, field=field, operator="in", values=values
        )


@dataclass
class PayloadTrafficRuleCondition(TrafficRuleCondition):
    def __init__(self, field: str, values: List[str]):
        """
        Method to create a new TrafficRuleCondition that is defined on a request payload

        :param field: name of the field specified
        :param values: values that are supposed to match those found in the field
        """
        super().__init__(
            field_source=FieldSource.PAYLOAD, field=field, operator="in", values=values
        )


@dataclass
class DefaultTrafficRule:
    """
    Class to create a new default TrafficRule based on no conditions and one or more routes

    :param routes: list of routes to send the request to
    """

    routes: List[str]

    _routes: List[str] = dataclasses.field(init=False, repr=False)

    @property
    def routes(self) -> List[str]:
        return self._routes

    @routes.setter
    def routes(self, routes: List[str]):
        self._routes = routes

    def to_open_api(self) -> OpenApiModel:
        self._verify_no_duplicate_routes()

        return caraml.routers.client.models.DefaultTrafficRule(
            routes=self.routes,
        )

    def _verify_no_duplicate_routes(self):
        route_id_counter = Counter(self.routes)
        most_common_route_id, max_frequency = route_id_counter.most_common(n=1)[0]
        if max_frequency > 1:
            raise caraml.routers.router.config.route.DuplicateRouteException(
                f"Routes with duplicate ids are specified for this traffic rule. Duplicate id: {most_common_route_id}"
            )


@dataclass
class TrafficRule:
    """
    Class to create a new TrafficRule based on a list of conditions and routes

    :param name: Name of TrafficRule, should be unique for every set of rules in a Router
    :param conditions: list of TrafficRuleConditions that need to ALL be satisfied before routing to the given routes
    :param routes: list of routes to send the request to should all the given conditions be met
    """

    name: str
    conditions: Union[List[TrafficRuleCondition], List[Dict[str, List[str]]]]
    routes: List[str]

    _name: str = dataclasses.field(init=False, repr=False)
    _conditions: Union[List[TrafficRuleCondition], List[Dict[str, List[str]]]] = (
        dataclasses.field(init=False, repr=False)
    )
    _routes: List[str] = dataclasses.field(init=False, repr=False)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def conditions(self):
        return self._conditions

    @conditions.setter
    def conditions(
        self, conditions: Union[List[TrafficRuleCondition], List[Dict[str, List[str]]]]
    ):
        if isinstance(conditions, list):
            if all(
                isinstance(condition, TrafficRuleCondition) for condition in conditions
            ):
                self._conditions = conditions
            elif all(isinstance(condition, dict) for condition in conditions):
                self._conditions = [
                    TrafficRuleCondition(**condition) for condition in conditions
                ]
            else:
                self._conditions = conditions
        else:
            self._conditions = conditions

    @property
    def routes(self) -> List[str]:
        return self._routes

    @routes.setter
    def routes(self, routes: List[str]):
        self._routes = routes

    def to_open_api(self) -> OpenApiModel:
        self._verify_no_duplicate_routes()

        return caraml.routers.client.models.TrafficRule(
            name=self.name,
            conditions=[
                traffic_rule_condition.to_open_api()
                for traffic_rule_condition in self.conditions
            ],
            routes=self.routes,
        )

    def _verify_no_duplicate_routes(self):
        route_id_counter = Counter(self.routes)
        most_common_route_id, max_frequency = route_id_counter.most_common(n=1)[0]
        if max_frequency > 1:
            raise caraml.routers.router.config.route.DuplicateRouteException(
                f"Routes with duplicate ids are specified for this traffic rule. Duplicate id: {most_common_route_id}"
            )
