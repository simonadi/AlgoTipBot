from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from time import time
from typing import TYPE_CHECKING
from typing import Optional
from typing import Union

from algosdk import transaction
from algosdk.util import algos_to_microalgos
from algosdk.util import microalgos_to_algos
from praw.models.reddit.comment import Comment
from praw.models.reddit.message import Message

from AlgoTipBot.clients import algod
from AlgoTipBot.clients import console
from AlgoTipBot.clients import redis
from AlgoTipBot.errors import FirstTransactionError
from AlgoTipBot.errors import InsufficientFundsError
from AlgoTipBot.errors import ZeroTransactionError
from AlgoTipBot.templates import INSUFFICIENT_FUNDS
from AlgoTipBot.templates import TIP_RECEIVED
from AlgoTipBot.templates import TRANSACTION_CONFIRMATION
from AlgoTipBot.templates import WITHDRAWAL_CONFIRMATION


class Transaction(ABC):
    """
    Abstract class to define the methods required for a
    transaction
    """
    @abstractmethod
    def valid(self) -> bool:
        pass

    @abstractmethod
    def send(self) -> "Transaction":
        pass

    @abstractmethod
    def confirmed(self) -> bool:
        pass

    @abstractmethod
    def save(self) -> None:
        pass

    @abstractmethod
    def send_confirmation(self) -> None:
        pass

    @abstractmethod
    def log(self) -> None:
        pass

    @abstractmethod
    def __hash__(self) -> int:
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

    def valid(self) -> bool:
        """
        """
        return True

    def send(self) -> "TipTransaction":
        """
        Perform checks to make sure that the transaction can be done
        before creating it and sending it

        Returns:
            Transaction: returns itself if the transaction was successfully
                         None otherwise
        """
        params = algod.suggested_params()
        self.fee = float(microalgos_to_algos(params.min_fee))

        if self.amount < 1e-6: raise ZeroTransactionError

        if (self.amount + self.fee + 0.1) > self.sender.wallet.balance: raise InsufficientFundsError(self.amount,
                                                                                                     self.sender.wallet.balance)

        if self.receiver.wallet.balance == 0 and amount < 0.1:
            raise FirstTransactionError(amount)

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

        return self

    def confirmed(self) -> bool:
        """
        Returns a boolean indicating whether or not the
        transaction is confirmed
        """
        txinfo = algod.pending_transaction_info(self.tx_id)
        return (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0)

    def save(self) -> None:
        """
        Saves the transaction's information to the Redis
        database
        """
        redis.incr("tx_id")
        redis_tx_id = redis.get("tx_id")
        redis.hmset(f"algotip-transactions:{redis_tx_id}", {"sender": self.sender.name,
                                                           "receiver": self.receiver.name,
                                                           "amount": self.amount,
                                                           "transaction_id": self.tx_id,
                                                           "fee": self.fee,
                                                           "time": self.time})

    def send_confirmation(self) -> None:
        """

        """
        self.sender.message("Tip confirmation",
                            TRANSACTION_CONFIRMATION.substitute(
                                amount=transaction.amount,
                                receiver=transaction.receiver.name
                    )
        )

        self.receiver.message(
            subject="AlgoTip",
            message=TIP_RECEIVED.substitute(sender=transaction.sender.name
                                                    if not transaction.anonymous
                                                    else "An anonymous redditor",
                                            amount=transaction.amount)
        )

    def log(self) -> None:
        """
        """
        pass

    def __hash__(self) -> int:
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

    def valid(self) -> bool:
        """
        """
        return True

    def send(self) -> "WithdrawTransaction":
        """

        """
        amount = self.sender.wallet.balance if self.amount == "all" else float(self.amount)
        close_account = (amount == self.sender.wallet.balance)

        params = algod.suggested_params()
        self.fee = float(microalgos_to_algos(params.min_fee))

        if self.amount < 1e-6: raise ZeroTransactionError

        if (self.amount + self.fee + (int(close_account)*0.1)) > self.sender.wallet.balance:
            raise InsufficientFundsError(amount, self.sender.wallet.balance)

        if Wallet("", self.destination).balance == 0 and amount < 0.1:
            raise FirstTransactionError(amount)

        if close_account:
            redis.delete(f"algotip-wallets:{self.sender.name}")
            amount = amount - self.fee

        tx = transaction.PaymentTxn(self.sender.wallet.public_key,
                                    params.min_fee,
                                    params.first,
                                    params.last,
                                    params.gh,
                                    self.destination,
                                    algos_to_microalgos(amount),
                                    note=str.encode(self.message),
                                    close_remainder_to=None if not close_account else self.destination,
                                    flat_fee=True)

        signed_tx = tx.sign(self.sender.wallet.private_key)

        algod.send_transaction(signed_tx)
        self.time = time()
        self.tx_id = signed_tx.transaction.get_txid()



        console.log(f"Transaction of {self.amount} Algos withdrawn by {self.sender.name} to address {self.destination}")

        return self

    def confirmed(self) -> bool:
        """

        """
        txinfo = algod.pending_transaction_info(self.tx_id)
        return (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0)

    def send_confirmation(self) -> None:
        """

        """
        self.trigger_event.reply(WITHDRAWAL_CONFIRMATION.substitute(amount=transaction.amount,
                                                                    address=transaction.destination))

    def save(self) -> None:
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

    def __hash__(self) -> int:
        """
        """
        return hash(self.tx_id)
