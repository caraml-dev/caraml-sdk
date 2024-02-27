
from common.utils import is_valid_project_name, get_mlp_url

import pytest


@pytest.mark.unit
def test_name_check():
    invalid_names = ["test-name,", "test,name", "test.name"]

    valid_names = ["test-name", "testname", "abc2"]

    for name in invalid_names:
        assert is_valid_project_name(name) is False
    for name in valid_names:
        assert is_valid_project_name(name) is True


@pytest.mark.unit
def test_get_mlp_url():
    inputs = ["http://console.ai.io/merlin/api", "http://merlin.dev/merlin/api", "http://console.ai/turing/api"]

    outputs = ["http://console.ai.io", "http://merlin.dev", "http://console.ai"]

    for url, mlp_url in zip(inputs, outputs):
        assert get_mlp_url(url) == mlp_url
    