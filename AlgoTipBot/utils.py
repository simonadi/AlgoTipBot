"""
Utility functions
"""

from clients import reddit, algod
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


# Comes from https://developer.algorand.org/docs/build-apps/hello_world/
def wait_for_confirmation(transaction_id, timeout):
    """
    Wait until the transaction is confirmed or rejected, or until 'timeout'
    number of rounds have passed.
    Args:
        transaction_id (str): the transaction to wait for
        timeout (int): maximum number of rounds to wait
    Returns:
        dict: pending transaction information, or throws an error if the transaction
            is not confirmed or rejected in the next timeout rounds
    """
    start_round = algod.status()["last-round"] + 1;
    current_round = start_round

    while current_round < start_round + timeout:
        try:
            pending_txn = algod.pending_transaction_info(transaction_id)
        except Exception:
            return
        if pending_txn.get("confirmed-round", 0) > 0:
            return pending_txn
        elif pending_txn["pool-error"]:
            raise Exception(
                'pool error: {}'.format(pending_txn["pool-error"]))
        algod.status_after_block(current_round)
        current_round += 1
    raise TimeoutError(
        'pending tx not found in timeout rounds, timeout value = : {}'.format(timeout))
