import re
from urllib.parse import urlparse


VALID_PROJECT_NAME_PATTERN = re.compile(r"[-a-z0-9]+") 
MERLIN_OR_TURING_URL_PREFIX_PATTERN = re.compile(r"(merlin|turing).*") 


def is_valid_project_name(name: str) -> bool:
    """
    Checks if inputted name for project and model is url-friendly
        - has to be lower case
        - can only contain character (a-z) number (0-9) and '-'
    """
    
    match = VALID_PROJECT_NAME_PATTERN.match(name)
    return (match is not None) and match.group(0) == name


def get_mlp_url(url: str) -> str:
    """
    Extracts MLP url from merlin/turing urls.
    """
    base_url = MERLIN_OR_TURING_URL_PREFIX_PATTERN.sub(url, "")
    return base_url