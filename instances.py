from algosdk.account import generate_account
from algosdk.v2_client import algod

from praw.models.reddit.message import Message
from praw.models.reddit.comment import Comment

from typing import Union

from dataclasses import dataclass

from redis import Redis

import os

import qrcode

from datetime import datetime

######################### Initialize Redis connection #########################

redis = Redis()

######################### Initialize Algod connection #########################

ALGOD_TOKEN = os.environ.get("ALGOD_TOKEN")
ALGOD_ADDRESS = "https://testnet-algorand.api.purestake.io/ps2"

headers = {
    "x-api-key": ALGOD_TOKEN
}

algod = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS, headers)


######################### Initialize Reddit connection #########################

client = praw.Reddit(
            "AlgorandTipBot",
            user_agent="AlgoTipBot"
)


@dataclass
class Wallet:
    private_key: str
    public_key: str

    @classmethod
    def generate(cls) -> "Wallet":
        """
        Generates a public/private key pair
        """
        private_key, public_key = generate_account()
        return cls(private_key, public_key)

    @classmethod
    def load(cls, username: str) -> "Wallet":
        """

        """
        wallet_dict = redis.hgetall(f"algotip-wallets:{username}")
        if wallet_dict is None:
            return None
        else:
            return cls(wallet_dict["private_key"], wallet_dict["public_key"])

    def save(self, username: str) -> None:
        """
        Saves the wallet information to the Redis 
        database
        """
        redis.hset(f"algotip-wallets:{username}", {"private_key": self.private_key,
                                                   "public_key": self.public_key})

    def qrcode(self) -> None:
        """

        """
        img = qrcode.make(address)
        img.show()

    @property
    def balance(self) -> float:
        """

        """
        account_info = algod.account_info(self.public_key)
        print(account_info)
        balance = float(microalgos_to_algos(account_info["amount-without-pending-rewards"])) # Show the balance with rewards
        return balance

    def __repr__(self) -> None:
        """
        """
        return WALLET_REPR.substitute(private_key=self.private_key,
                                      public_key=self.public_key,
                                      balance=self.balance)

@dataclass
class Transaction:
    sender: User
    receiver: User
    amount: float
    message: str
    trigger_event: Union[Message, Comment]
    tx_id: str = None
    fee: float = None
    time: int = None

    def send(self, close_account: bool = False):
        """

        """
        params = algod.suggested_params()
        self.fee = float(microalgos_to_algos(params.min_fee))
        tx = transaction.PaymentTxn(self.sender.wallet.public_key,
                                    params.min_fee,
                                    params.first,
                                    params.last,
                                    params.gh,
                                    self.receiver.wallet.public_key,
                                    self.amount,
                                    note=self.message,
                                    close_remainder_to=None if not close_account else "close",
                                    flat_fee=True)

        signed_tx = tx.sign(self.sender.wallet.private_key)

        algod.send_transaction(signed_tx)
        self.time = time()
        self.tx_id = signed_tx.transaction.get_txid()

        console.log(f"Transaction of {self.amount} Algos sent by {self.sender.name} to {self.receiver.name}")

    def confirmed(self):
        """

        """
        last_round = client.status().get('last-round')
        txinfo = client.pending_transaction_info(txid)
        return (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0)

    def save(self):
        """

        """
        redis.incr("tx_id")
        redis_tx_id = redis.get("tx_id")
        redis.hset(f"algotip-transactions:{redis_tx_id}", {"sender": self.sender.name,
                                                           "receiver": self.receiver.name,
                                                           "amount": self.amount,
                                                           "transaction_id": self.tx_id,
                                                           "fee": self.fee,
                                                           "time": self.time})

class User:
    """
    """
    def __init__(self, name: str) -> None:
        """

        """
        self.name = name

        wallet = Wallet.load(name)
        if wallet is None:
            wallet = Wallet.generate(name)
        
        self.wallet = wallet
        self.wallet.save(name)


    def send(self, other_user: "User", amount: float, message: str) -> bool:
        """
        """
        transaction = Transaction(self, other_user, amount, message)
        transaction.send()