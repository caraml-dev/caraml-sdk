
from common.utils import is_valid_project_name

import pytest


@pytest.mark.unit
def test_name_check():
    invalid_names = ["test-name,", "test,name", "test.name"]

    valid_names = ["test-name", "testname", "abc2"]

    for name in invalid_names:
        assert is_valid_project_name(name) is False
    for name in valid_names:
        assert is_valid_project_name(name) is True