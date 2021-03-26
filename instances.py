from algosdk.account import generate_account
from algosdk.v2client import algod
from algosdk.util import microalgos_to_algos

from praw.models.reddit.message import Message
from praw.models.reddit.comment import Comment

from typing import Union

from dataclasses import dataclass

from redis import Redis

import praw

import os

import qrcode

from datetime import datetime

from templates import WALLET_REPR, WALLET_CREATED
from rich.console import Console

console = Console()

######################### Initialize Redis connection #########################

REDIS_PW = os.environ.get("REDIS_PW")
redis = Redis(password=REDIS_PW, decode_responses=True)

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
        if not wallet_dict:
            return None
        else:
            return cls(wallet_dict["private_key"], wallet_dict["public_key"])

    def save(self, username: str) -> None:
        """
        Saves the wallet information to the Redis
        database
        """
        redis.hmset(f"algotip-wallets:{username}", {"private_key": self.private_key,
                                                    "public_key": self.public_key})

    @property
    def qrcode(self) -> None:
        """

        """
        return f"https://api.qrserver.com/v1/create-qr-code/?data={self.public_key}&size=220x220&margin=4"

    @property
    def balance(self) -> float:
        """

        """
        account_info = algod.account_info(self.public_key)
        balance = float(microalgos_to_algos(account_info["amount"]))
        return balance

    def __repr__(self) -> None:
        """
        """
        return WALLET_REPR.substitute(private_key=self.private_key,
                                      public_key=self.public_key,
                                      balance=self.balance,
                                      qr_code_link=self.qrcode)

class User:
    """
    """
    def __init__(self, name: str) -> None:
        """

        """
        self.name = name

        wallet = Wallet.load(name)
        if wallet is None:
            wallet = Wallet.generate()
            console.log(WALLET_CREATED.substitute(user=name,
                                                  public_key=wallet.public_key))

        self.wallet = wallet
        self.wallet.save(name)


    def send(self, other_user: "User", amount: float, message: str) -> Transaction:
        """
        """
        transaction = TipTransaction(self, other_user, amount, message)
        transaction.send()
        return transaction

    def withdraw(self, address: str, amount: float) -> Transaction:
        """

        """
        # transaction = WithdrawTransaction(self, )
        pass