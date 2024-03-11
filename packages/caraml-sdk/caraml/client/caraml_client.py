from typing import List
import urllib3
import logging

from caraml.version import VERSION as caraml_sdk_version

from caraml.models.merlin_client import MerlinClient as ModelsClient
# from caraml.routers.session import TuringSession as RoutersClient
from caraml.mlp.mlp_client import MLPClient


logger = logging.getLogger("caraml_client")


class CaraMLClient:
    _mlp_url_suffix = "/api"
    _models_url_suffix = "/api/merlin"
    _routers_url_suffix = "/api/turing"

    def __init__(self, caraml_url: str, use_google_oauth: bool = True):
        self._caraml_url = caraml_url

        # create clients for all caraml modules.
        self._mlp_client = MLPClient(
            self._caraml_url + self._mlp_url_suffix,
            use_google_oauth=use_google_oauth,
            caraml_sdk_version=caraml_sdk_version,
        )
        self._models_client = ModelsClient(
            self._caraml_url + self._models_url_suffix,
            use_google_oauth=use_google_oauth,
            caraml_sdk_version=caraml_sdk_version,
            mlp_client=self._mlp_client,
        )
        # self._routers_client = RoutersClient(
        #     self._caraml_url + self._models_url_suffix,
        #     use_google_oauth=use_google_oauth,
        #     caraml_sdk_version=caraml_sdk_version,
        #     mlp_client=self._mlp_client,
        # )

        # Create a map to find and use all CaraML component methods to proxy to corresponding component.
        self._caraml_methods = {}

        # Add in the order of MLP , Merlin, Turing. This way, duplicate methods will be ignored.
        self._mlp_methods = [
            method_name
            for method_name in dir(self._mlp_client)
            if callable(getattr(self._mlp_client, method_name))
            and not method_name.startswith("_")
        ]
        self._add_caraml_methods(self._mlp_methods, self._mlp_client)
        logger.debug(
            f"Registered {len(self._mlp_methods)} from MLP. methods: {self._mlp_methods}"
        )

        self._models_methods = [
            method_name
            for method_name in dir(self._models_client)
            if callable(getattr(self._models_client, method_name))
            and not method_name.startswith("_")
        ]
        self._add_caraml_methods(self._models_methods, self._models_client)
        logger.debug(
            f"Registered {len(self._models_methods)} from Models. methods: {self._models_methods}"
        )

        # self._routers_methods = [
        #     method_name
        #     for method_name in dir(self._routers_client)
        #     if callable(getattr(self._routers_client, method_name))
        #     and not method_name.startswith("_")
        # ]
        # self._add_caraml_methods(self._routers_methods, self._routers_client)
        # logger.debug(
        #     f"Registered {len(self._routers_methods)} from Routers. methods: {self._routers_methods}"
        # )

        for method_name, client in self._caraml_methods.items():
            self._create_caraml_methods(method_name, client)

    def _add_caraml_methods(self, methods: List[str], object):
        for method in methods:
            if method not in self._caraml_methods:
                self._caraml_methods[method] = object

    def _create_caraml_methods(self, method_name, client):
        def method(*args, **kwargs):
            f = getattr(client, method_name)
            return f(*args, **kwargs)

        logger.debug(f"setting method name: {method_name} using client: {client}")
        method.__doc__ = f"{getattr(client, method_name).__doc__} \n Generated from {client.__class__}"
        setattr(self, method_name, method)

    @property
    def url(self):
        return self._caraml_url
