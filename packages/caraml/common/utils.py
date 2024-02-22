import re


VALID_PROJECT_NAME_PATTERN = re.compile(r"[-a-z0-9]+") 


def is_valid_project_name(name: str) -> bool:
    """
    Checks if inputted name for project and model is url-friendly
        - has to be lower case
        - can only contain character (a-z) number (0-9) and '-'
    """
    
    match = VALID_PROJECT_NAME_PATTERN.match(name)
    return (match is not None) and match.group(0) == name
