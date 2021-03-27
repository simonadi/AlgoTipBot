"""
TODO
"""
from clients import reddit

def is_float(value: str) -> bool:
    """
    Utility function to know whether or not a given string
    contains a valid float

    Args:
        value: string to check
    Returns:
        Boolean:
            True if string can be converted to float
            False otherwise
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def valid_user(username: str) -> bool:
    """
    Checks whether or not the username is valid

    Args:
        username: username to check
    Returns:
        Boolean:
            True if username exists
            False otherwise
    """
    try:
        reddit.redditor(username).id
    except NotFound:
        return False
    return True
