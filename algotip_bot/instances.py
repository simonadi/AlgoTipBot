"""
TODO
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from time import time_ns
from typing import Optional

from algosdk import transaction
from algosdk.account import generate_account
from algosdk.mnemonic import from_private_key
from algosdk.util import algos_to_microalgos, microalgos_to_algos

from algotip_bot.clients import algod, console, reddit, redis
from algotip_bot.errors import (FirstTransactionError, InsufficientFundsError,
                               ZeroTransactionError)
from algotip_bot.templates import (NEW_USER, TIP_RECEIVED,
                                  TRANSACTION_CONFIRMATION, WALLET_REPR,
                                  WITHDRAWAL_CONFIRMATION)


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
        if not wallet_dict: # pylint: disable=R1705
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

        if wallet is None:
            wallet = Wallet.load(self.user_id)

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
        return self.name in moderators

    def send(self,
             other_user: "User",
             amount: float,
             note: str,
             anonymous: bool = False) -> Optional["Transaction"]:
        """
        Send Algos to the targeted user

        Args:
            other_user:
            amount:
            note:
            event:
            anonymous:
        Returns:
            trsctn: the Transaction instance representing the transaction that was sent
        """
        trsctn = TipTransaction(self, other_user, amount, note, anonymous)
        trsctn.validate()
        trsctn.send()
        return trsctn

    def withdraw(self, amount: float, address: str, note: str) -> Optional["Transaction"]:
        """
        Withdraw Algos to the targeted address

        Args:
            amount:
            address:
            note:
        Returns:
            trsctn: the Transaction instance representing the transaction that was sent
        """
        trsctn = WithdrawTransaction(self, address, amount, note)
        trsctn.validate()
        trsctn.send()
        return trsctn

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
    def validate(self) -> bool: # pylint: disable=C0116
        pass

    @abstractmethod
    def send(self) -> "Transaction": # pylint: disable=C0116
        pass

    @abstractmethod
    def confirmed(self) -> bool: # pylint: disable=C0116
        pass

    @abstractmethod
    def send_confirmation(self) -> None: # pylint: disable=C0116
        pass

    @abstractmethod
    def log(self) -> None: # pylint: disable=C0116
        pass

    @abstractmethod
    def __hash__(self) -> int: # pylint: disable=C0116
        pass

@dataclass
class TipTransaction(Transaction): # pylint: disable=R0902
    """
    Subclass of the Transaction class containing
    a tip transaction
    """
    sender: "User"
    receiver: "User"
    amount: float
    message: str
    anonymous: bool
    tx_id: str = None
    redis_tx_id: int = None
    fee: float = None
    time: int = None
    params = None

    def validate(self) -> bool:
        """
        Check that the transaction is valid, otherwise raise
        a custom error indicating the issue.
        """
        self.params = algod.suggested_params()
        self.fee = float(microalgos_to_algos(self.params.min_fee))

        if self.amount < 1e-6:
            raise ZeroTransactionError

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
        txn = transaction.PaymentTxn(self.sender.wallet.public_key,
                                    params.min_fee,
                                    params.first,
                                    params.last,
                                    params.gh,
                                    self.receiver.wallet.public_key,
                                    algos_to_microalgos(self.amount),
                                    note=str.encode(self.message),
                                    flat_fee=True)

        signed_txn = txn.sign(self.sender.wallet.private_key)

        algod.send_transaction(signed_txn)
        self.time = time_ns() * 1e-6
        self.tx_id = signed_txn.transaction.get_txid()
        self.redis_tx_id = redis.incr("transaction-id")

        console.log(f"Transaction #{self.redis_tx_id} sent by {self.sender.name} to {self.receiver.name}")

    def confirmed(self) -> bool:
        """
        Returns a boolean indicating whether or not the
        transaction is confirmed
        """
        txinfo = algod.pending_transaction_info(self.tx_id)
        return txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0


    def send_confirmation(self) -> None:
        """
        Send a message to confirm the sender of the
        transaction confirmation and to inform the receiver
        that someone tipped him
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
        """
        Log the transaction to the Redis DB
        """
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
class WithdrawTransaction(Transaction): # pylint: disable=R0902
    """
    Subclass of the Transaction class containing a
    withdrawal

    """
    sender: "User"
    destination: str
    amount: float
    message: str
    tx_id: str = None
    close_account: bool = False
    redis_tx_id: int = None
    fee: float = None
    time: int = None
    params = None

    def validate(self) -> bool:
        """
        Chech that the transaction is valid, otherwise raise an error
        that indicates the type of issue
        """
        self.params = algod.suggested_params()
        self.fee = float(microalgos_to_algos(self.params.min_fee))

        self.amount = self.sender.wallet.balance if self.amount == "all" else float(self.amount)
        self.close_account = (self.amount == self.sender.wallet.balance)

        if self.close_account:
            self.amount = self.amount - self.fee

        if self.amount < 1e-6:
            raise ZeroTransactionError

        if (self.amount + self.fee + (int(not self.close_account)*0.1)) > self.sender.wallet.balance:
            raise InsufficientFundsError(self.amount, self.sender.wallet.balance)

        if Wallet("", self.destination).balance == 0 and self.amount < 0.1:
            raise FirstTransactionError(self.amount)

    def send(self) -> "WithdrawTransaction":
        """
        Send the transaction with the parameters given during initialization of the class
        Gets the redis tx id to preserve creation order
        (TODO : create the transaction with the send time and update it when confirmed
                with confirmation time)
        """
        params = self.params

        txn = transaction.PaymentTxn(self.sender.wallet.public_key,
                                     params.min_fee,
                                     params.first,
                                     params.last,
                                     params.gh,
                                     self.destination,
                                     algos_to_microalgos(self.amount),
                                     note=str.encode(self.message),
                                     close_remainder_to=None if not self.close_account else self.destination,
                                     flat_fee=True)

        signed_txn = txn.sign(self.sender.wallet.private_key)

        algod.send_transaction(signed_txn)
        self.time = time_ns() * 1e-6
        self.tx_id = signed_txn.transaction.get_txid()
        self.redis_tx_id = redis.incr("transaction-id")

        console.log(f"Withdrawal #{self.redis_tx_id} sent by {self.sender.name}")

    def confirmed(self) -> bool:
        """
        Checks if the transaction has been confirmed
        Returns:
            Bool:
                True if the transaction is confirmed
                False otherwise
        """
        txinfo = algod.pending_transaction_info(self.tx_id)
        return txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0

    def send_confirmation(self) -> None:
        """
        Sends a message to the Reddit user to confirm the withdrawal,
        and give a link to AlgoExplorer to have a proof of transaction
        """
        self.sender.message("Withdrawal confirmations",
                            WITHDRAWAL_CONFIRMATION.substitute(amount=self.amount,
                                                               address=self.destination,
                                                               transaction_id=self.tx_id))

    def log(self) -> None:
        """
        Logs the confirmation of the withdrawal to the console and
        to the database by adding a transaction record
        """
        console.log(f"Withdrawal #{self.redis_tx_id} confirmed")

        redis.hmset(f"transaction:{self.redis_tx_id}", {"user": self.sender.user_id,
                                                    "amount": self.amount,
                                                    "transaction-id": self.tx_id,
                                                    "fee": self.fee})

        redis.zadd("withdrawals", {self.redis_tx_id: self.time})

    def __hash__(self) -> int:
        """
        Returns a hash of the Algo transaction ID (int)
        Allows the use of this class in sets and dictionaries
        """
        return hash(self.tx_id)
