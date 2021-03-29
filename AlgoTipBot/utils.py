"""
Utility functions
"""

from clients import reddit
from prawcore.exceptions import NotFound

COMMENT_COMMANDS = {"!atip"}
SUBREDDITS = {"algorand", "algorandofficial", "cryptocurrency", "bottesting"}
COMMENT_CACHE = set()

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

def stream():
    """
    Fetches the unread items in the inbox and all comments in the
    targeted subreddits that contain an AlgoTip command
    Adds the comments to a cache to know which ones were already dealt with
    """
    inbox_unread = set(reddit.inbox.unread())
    comments = {comment for comment in reddit.subreddit("+".join(SUBREDDITS)).comments(limit=100)
                        if any(command in comment.body for command in COMMENT_COMMANDS)
                        and comment.id not in COMMENT_CACHE}

    COMMENT_CACHE.update({comment.id for comment in comments})

    return set.union(inbox_unread, comments)
