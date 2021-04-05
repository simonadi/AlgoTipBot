"""
TODO
"""

class InvalidCommandError(Exception):
    def __init__(self, command: str) -> None:
        self.command = command

class ZeroTransactionError(Exception):
    pass

class InsufficientFundsError(Exception):
    def __init__(self, amount: float, balance: float) -> None:
        self.amount, self.balance = amount, balance

class InvalidUserError(Exception):
    def __init__(self, username: str) -> None:
        self.username = username

class FirstTransactionError(Exception):
    def __init__(self, amount: float) -> None:
        self.amount = amount

class InvalidSubredditError(Exception):
    def __init__(self, subreddit: str) -> None:
        self.subreddit = subreddit

class NotModeratorError(Exception):
    pass
