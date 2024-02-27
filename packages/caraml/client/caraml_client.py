
import urllib3

from version import VERSION as caraml_sdk_version

from models.merlin_client import MerlinClient as ModelsClient
from routers.session import TuringSession as RoutersClient
from mlp.mlp_client import MLPClient


class CaraMLClient:
    _mlp_url_suffix = "/"
    _models_url_suffix = "/merlin/api"
    _routers_url_suffix = "/turing/api"

    def __init__(self, caraml_url: str, use_google_oauth: bool = True):
        self._caraml_url = caraml_url

        # create clients for all caraml modules.
        self._mlp_client = MLPClient(self._caraml_url + self._mlp_url_suffix, caraml_sdk_version=caraml_sdk_version)
        self._models_client = ModelsClient(self._caraml_url + self._models_url_suffix,
                                           caraml_sdk_version=caraml_sdk_version,
                                           mlp_client=self._mlp_client)
        self._routers_client = RoutersClient(self._caraml_url + self._models_url_suffix,
                                           caraml_sdk_version=caraml_sdk_version,
                                           mlp_client=self._mlp_client)

    @property
    def url(self):
        return self._caraml_url

