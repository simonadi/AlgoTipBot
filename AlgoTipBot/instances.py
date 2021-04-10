from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from time import time_ns
from typing import TYPE_CHECKING
from typing import Optional
from typing import Union

from algosdk import transaction
from algosdk.account import generate_account
from algosdk.mnemonic import from_private_key
from algosdk.util import algos_to_microalgos
from algosdk.util import microalgos_to_algos
from praw.models.reddit.comment import Comment
from praw.models.reddit.message import Message

from AlgoTipBot.clients import algod
from AlgoTipBot.clients import console
from AlgoTipBot.clients import reddit
from AlgoTipBot.clients import redis
from AlgoTipBot.errors import FirstTransactionError
from AlgoTipBot.errors import InsufficientFundsError
from AlgoTipBot.errors import ZeroTransactionError
from AlgoTipBot.templates import INSUFFICIENT_FUNDS
from AlgoTipBot.templates import NEW_USER
from AlgoTipBot.templates import TIP_RECEIVED
from AlgoTipBot.templates import TRANSACTION_CONFIRMATION
from AlgoTipBot.templates import WALLET_CREATED
from AlgoTipBot.templates import WALLET_REPR
from AlgoTipBot.templates import WITHDRAWAL_CONFIRMATION


@dataclass
class Wallet:
    """
    Class representing an ALGO wallet, containing helper methods
    """
    private_key: str
    public_key: str

    @classmethod
    def generate(cls) -> "Wallet":
        """
        Generates a public/private key pair

        Returns:
            wallet: an instance of the class Wallet with the generated keys
        """
        private_key, public_key = generate_account()
        return cls(private_key, public_key)

    @classmethod
    def load(cls, user_id: int) -> Optional["Wallet"]:
        """
        Loads the wallet keys from the given user

        Args:
            user_id: the DB user-id for which we want the keys
        Returns:
            wallet:
                None if the wallet information isn't found in the DB
                An instance of the class Wallet with the fetched keys otherwise
        """
        wallet_dict = redis.hgetall(f"wallets:{user_id}")
        if not wallet_dict:
            return None
        else:
            return cls(wallet_dict["private_key"], wallet_dict["public_key"])

    def log(self, user: "User") -> None:
        """
        Saves the wallet information to the Redis
        database

        Args:
            user: an instance of User corresponding to the wallet owner
        """
        console.log(f"Wallet created for user {user.name} (#{user.user_id})")
        redis.hmset(f"wallets:{user.user_id}", {"private_key": self.private_key,
                                                "public_key": self.public_key})

    @property
    def qrcode(self) -> None:
        """
        Returns the link to a QR code created from the public key of this wallet
        """
        return f"https://api.qrserver.com/v1/create-qr-code/?data={self.public_key}&size=220x220&margin=4"

    @property
    def balance(self) -> float:
        """
        Returns the balance of the wallet

        Returns:
            balance: the balance of the wallet as a float, in Algos
        """
        account_info = algod.account_info(self.public_key)
        balance = float(microalgos_to_algos(account_info["amount"]))
        return balance

    def __repr__(self) -> str:
        """
        Returns all information about the wallet in a string

        Returns:
            str
        """
        return WALLET_REPR.substitute(private_key=from_private_key(self.private_key),
                                      public_key=self.public_key,
                                      balance=self.balance,
                                      qr_code_link=self.qrcode)

class User:
    """
    Class representing a Reddit user
    """
    def __init__(self, name: str, wallet: Wallet = None) -> None:
        """
        TODO: doc
        """
        self.name = name.lower()

        if (user_id:=redis.get(f"users:{self.name}")) is None:
            user_id = redis.incr("user-id")
            self.user_id = user_id
            self.log()
        else:
            self.user_id = user_id

        self.new = False

        if wallet is None: wallet = Wallet.load(self.user_id)

        if wallet is None:
            self.new = True
            wallet = Wallet.generate()
            reddit.redditor(self.name).message("Wallet created", NEW_USER.substitute(wallet=str(wallet)))
            wallet.log(self)

        self.wallet = wallet

    def is_moderator(self, subreddit: str) -> bool:
        """
        Checks if the user is a moderator of the given subreddit

        Args:
            subreddit: name of the subreddit
        Returns:
            bool:
                True if the user is a mod
                False otherwise
        """
        moderators = set(reddit.subreddit(subreddit).moderator())
        moderators = {redditor.name.lower() for redditor in moderators}
        return (self.name in moderators)

    def send(self, other_user: "User", amount: float, note: str, event, anonymous: bool = False) -> Optional["Transaction"]:
        """
        Send Algos to the targeted user

        Args:
            other_user:
            amount:
            note:
            event:
            anonymous:
        Returns:
            transaction: the Transaction instance representing the transaction that was sent
        """
        transaction = TipTransaction(self, other_user, amount, note, event, anonymous)
        transaction.validate()
        transaction.send()
        return transaction

    def withdraw(self, amount: float, address: str, note: str, event) -> Optional["Transaction"]:
        """
        Withdraw Algos to the targeted address

        Args:
            amount:
            address:
            note:
            event:
        Returns:
            transaction: the Transaction instance representing the transaction that was sent
        """
        transaction = WithdrawTransaction(self, address, amount, note, event)
        transaction.validate()
        transaction.send()
        return transaction

    def message(self, subject: str, message: str) -> None:
        """
        Messages the user on Reddit

        Arguments:
            subject: subject of the PM
            message: body of the PM
        """
        reddit.redditor(self.name).message(subject, message)

    def log(self):
        """
        Log the user creation in the console and save it in the DB
        """
        console.log(f"New user : {self.name} (#{self.user_id})")
        redis.set(f"users:{self.name}", self.user_id)


class Transaction(ABC):
    """
    Abstract class to define the methods required for a
    transaction
    """
    @abstractmethod
    def validate(self) -> bool:
        pass

    @abstractmethod
    def send(self) -> "Transaction":
        pass

    @abstractmethod
    def confirmed(self) -> bool:
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
    redis_tx_id: int = None
    fee: float = None
    time: int = None

    def validate(self) -> bool:
        """
        """
        self.params = algod.suggested_params()
        self.fee = float(microalgos_to_algos(self.params.min_fee))

        if self.amount < 1e-6: raise ZeroTransactionError

        if (self.amount + self.fee + 0.1) > self.sender.wallet.balance:
            raise InsufficientFundsError(self.amount,
                                         self.sender.wallet.balance)

        if self.receiver.wallet.balance == 0 and self.amount < 0.1:
            raise FirstTransactionError(self.amount)

    def send(self) -> "TipTransaction":
        """
        Perform checks to make sure that the transaction can be done
        before creating it and sending it

        Returns:
            Transaction: returns itself if the transaction was successfully
                         None otherwise
        """
        params = self.params
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
        self.time = time_ns() * 1e-6
        self.tx_id = signed_tx.transaction.get_txid()
        self.redis_tx_id = redis.incr("transaction-id")

        console.log(f"Transaction #{self.redis_tx_id} sent by {self.sender.name} to {self.receiver.name}")

    def confirmed(self) -> bool:
        """
        Returns a boolean indicating whether or not the
        transaction is confirmed
        """
        txinfo = algod.pending_transaction_info(self.tx_id)
        return (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0)

    def send_confirmation(self) -> None:
        """

        """
        self.sender.message("Tip confirmation",
                            TRANSACTION_CONFIRMATION.substitute(
                                amount=self.amount,
                                receiver=self.receiver.name,
                                transaction_id=self.tx_id
                    )
        )

        self.receiver.message(
            subject="AlgoTip",
            message=TIP_RECEIVED.substitute(sender=self.sender.name
                                                    if not self.anonymous
                                                    else "An anonymous redditor",
                                            amount=self.amount)
        )

    def log(self) -> None:

        redis_tx_id = redis.incr("transaction-id")

        console.log(f"Transaction #{self.redis_tx_id} confirmed")

        redis.hmset(f"transaction:{self.redis_tx_id}", {"sender": self.sender.user_id,
                                                    "receiver": self.receiver.user_id,
                                                    "amount": self.amount,
                                                    "transaction-id": self.tx_id,
                                                    "fee": self.fee})

        redis.zadd("tips", {self.redis_tx_id: self.time})

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
    close_account: bool = False
    redis_tx_id: int = None
    fee: float = None
    time: int = None

    def validate(self) -> bool:
        """
        """
        self.params = algod.suggested_params()
        self.fee = float(microalgos_to_algos(self.params.min_fee))

        self.amount = self.sender.wallet.balance if self.amount == "all" else float(self.amount)
        self.close_account = (self.amount == self.sender.wallet.balance)

        if self.close_account:
            self.amount = self.amount - self.fee

        if self.amount < 1e-6: raise ZeroTransactionError

        if (self.amount + self.fee + (int(not self.close_account)*0.1)) > self.sender.wallet.balance:
            raise InsufficientFundsError(self.amount, self.sender.wallet.balance)

        if Wallet("", self.destination).balance == 0 and self.amount < 0.1:
            raise FirstTransactionError(self.amount)

    def send(self) -> "WithdrawTransaction":
        """

        """
        params = self.params

        tx = transaction.PaymentTxn(self.sender.wallet.public_key,
                                    params.min_fee,
                                    params.first,
                                    params.last,
                                    params.gh,
                                    self.destination,
                                    algos_to_microalgos(self.amount),
                                    note=str.encode(self.message),
                                    close_remainder_to=None if not self.close_account else self.destination,
                                    flat_fee=True)

        signed_tx = tx.sign(self.sender.wallet.private_key)

        algod.send_transaction(signed_tx)
        self.time = time_ns() * 1e-6
        self.tx_id = signed_tx.transaction.get_txid()
        self.redis_tx_id = redis.incr("transaction-id")

        console.log(f"Withdrawal #{self.redis_tx_id} sent by {self.sender.name}")

    def confirmed(self) -> bool:
        """

        """
        txinfo = algod.pending_transaction_info(self.tx_id)
        return (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0)

    def send_confirmation(self) -> None:
        """

        """
        self.trigger_event.reply(WITHDRAWAL_CONFIRMATION.substitute(amount=self.amount,
                                                                    address=self.destination,
                                                                    transaction_id=self.tx_id))

    def log(self) -> None:
        console.log(f"Withdrawal #{self.redis_tx_id} confirmed")

        redis.hmset(f"transaction:{self.redis_tx_id}", {"user": self.sender.user_id,
                                                    "amount": self.amount,
                                                    "transaction-id": self.tx_id,
                                                    "fee": self.fee})

        redis.zadd("withdrawals", {self.redis_tx_id: self.time})

    def __hash__(self) -> int:
        """
        """
        return hash(self.tx_id)
