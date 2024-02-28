import re
from urllib.parse import urlparse


VALID_PROJECT_NAME_PATTERN = re.compile(r"[a-z][a-z0-9-_]*")


def is_valid_project_name(name: str) -> bool:
    """
    Checks if inputted name for project and model is url-friendly
        - has to be lower case
        - start with lower case
        - can only contain character (a-z) number (0-9) and '-', '_'
    """

    match = VALID_PROJECT_NAME_PATTERN.match(name)
    return (match is not None) and match.group(0) == name


def get_mlp_url(url: str, scheme: str = "http") -> str:
    """
    Extracts MLP url from merlin/turing urls.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if parsed_url.scheme:
        scheme = parsed_url.scheme
    return f"{scheme}://{domain}"
