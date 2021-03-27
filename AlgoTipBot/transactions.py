from abc import ABC, abstractmethod
from dataclasses import dataclass

from clients import redis, algod, reddit

from typing import Union

from praw.models.reddit.message import Message
from praw.models.reddit.comment import Comment

from algosdk import transaction
from algosdk.util import microalgos_to_algos, algos_to_microalgos

from time import time

from templates import INSUFFICIENT_FUNDS

from rich.console import Console

console = Console()

class Transaction(ABC):

    @abstractmethod
    def send(self) -> "Transaction":
        pass

    @abstractmethod
    def confirmed(self) -> None:
        pass

    @abstractmethod
    def save(self) -> None:
        pass

    @abstractmethod
    def log(self) -> None:
        pass


@dataclass
class TipTransaction(Transaction):
    sender: "User"
    receiver: "User"
    amount: float
    message: str
    trigger_event: Union[Message, Comment]
    anonymous: bool
    tx_id: str = None
    fee: float = None
    time: int = None

    def send(self):
        """

        """
        params = algod.suggested_params()
        self.fee = float(microalgos_to_algos(params.min_fee))

        if (self.amount + self.fee) > self.sender.wallet.balance:
            self.trigger_event.reply(INSUFFICIENT_FUNDS.substitue(balance=self.sender.wallet.balance,
                                                                  amount=self.amount))

        tx = transaction.PaymentTxn(self.sender.wallet.public_key,
                                    params.min_fee,
                                    params.first,
                                    params.last,
                                    params.gh,
                                    self.receiver.wallet.public_key,
                                    algos_to_microalgos(self.amount),
                                    note=str.encode(self.message),
                                    flat_fee=True)

        signed_tx = tx.sign(self.sender.wallet.private_key)

        algod.send_transaction(signed_tx)
        self.time = time()
        self.tx_id = signed_tx.transaction.get_txid()

        console.log(f"Transaction of {self.amount} Algos sent by {self.sender.name} to {self.receiver.name}")

    def confirmed(self):
        """

        """
        txinfo = algod.pending_transaction_info(self.tx_id)
        return (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0)

    def save(self):
        """

        """
        redis.incr("tx_id")
        redis_tx_id = redis.get("tx_id")
        redis.hmset(f"algotip-transactions:{redis_tx_id}", {"sender": self.sender.name,
                                                           "receiver": self.receiver.name,
                                                           "amount": self.amount,
                                                           "transaction_id": self.tx_id,
                                                           "fee": self.fee,
                                                           "time": self.time})

    def log(self):
        """
        """
        pass

    def __hash__(self):
        return hash(self.tx_id)

@dataclass
class WithdrawTransaction(Transaction):
    sender: "User"
    destination: str
    amount: float
    message: str
    trigger_event: Union[Message, Comment]
    tx_id: str = None
    fee: float = None
    time: int = None

    def send(self):
        """

        """
        amount = self.sender.wallet.balance if self.amount == "all" else float(self.amount)
        close_account = (amount == self.sender.wallet.balance)

        params = algod.suggested_params()
        self.fee = float(microalgos_to_algos(params.min_fee))

        if (not close_account) and (amount > (self.sender.wallet.balance + self.fee)):
            self.trigger_event.reply(INSUFFICIENT_FUNDS.substitue(balance=self.sender.wallet.balance,
                                                                  amount=amount))

        tx = transaction.PaymentTxn(self.sender.wallet.public_key,
                                    params.min_fee,
                                    params.first,
                                    params.last,
                                    params.gh,
                                    self.destination,
                                    algos_to_microalgos(amount),
                                    note=str.encode(self.message),
                                    close_remainder_to=None if not close_account else "close",
                                    flat_fee=True)

        signed_tx = tx.sign(self.sender.wallet.private_key)

        algod.send_transaction(signed_tx)
        self.time = time()
        self.tx_id = signed_tx.transaction.get_txid()

        console.log(f"Transaction of {self.amount} Algos withdrawn by {self.sender.name} to address {self.destination}")

    def confirmed(self):
        """

        """
        txinfo = algod.pending_transaction_info(self.tx_id)
        return (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0)

    def save(self):
        """

        """
        redis.incr("tx_id")
        redis_tx_id = redis.get("tx_id")
        redis.hmset(f"algotip-withdrawals:{redis_tx_id}", {"user": self.sender.name,
                                                          "amount": self.amount,
                                                          "transaction_id": self.tx_id,
                                                          "fee": self.fee,
                                                          "time": self.time})

    def log(self):
        """
        """
        pass

    def __hash__(self):
        """
        """
        return hash(self.tx_id)
