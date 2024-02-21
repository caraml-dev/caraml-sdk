
import urllib3

from version import VERSION


class CaraMLClient:
    _mlp_url_prefix = "/mlp"
    _models_url_prefix = "/merlin"
    _routers_url_prefix = "/turing"

    def __init__(self, caraml_url: str, use_google_oauth: bool = True):
        self._caraml_url = caraml_url

        # create clients for all caraml modules.

    @property
    def url(self):
        return self._caraml_url

