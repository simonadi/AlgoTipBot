"""
TODO
"""

class InvalidCommandError(Exception):
    def __init__(self, command: str) -> None:
        selF.command = command

class ZeroTransactionError(Exception):
    pass

class InsufficientFundsError(Exception):
    def __init__(self, amount: float, balance: float) -> None:
        self.amount, self.balance = amount, balance
