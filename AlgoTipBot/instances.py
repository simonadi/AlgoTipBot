from dataclasses import dataclass
from typing import Union, Optional

import qrcode
from algosdk.account import generate_account
from algosdk.mnemonic import from_private_key
from algosdk.util import microalgos_to_algos
from clients import algod, reddit, redis
from rich.console import Console
from templates import NEW_USER, WALLET_CREATED, WALLET_REPR
from transactions import TipTransaction, Transaction, WithdrawTransaction

console = Console()

@dataclass
class Wallet:
    """
    """
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
    def load(cls, username: str) -> Optional["Wallet"]:
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

    def __repr__(self) -> str:
        """
        """
        return WALLET_REPR.substitute(private_key=from_private_key(self.private_key),
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
        self.new = False

        wallet = Wallet.load(name)
        if wallet is None:
            self.new = True
            wallet = Wallet.generate()
            reddit.redditor(name).message("Wallet created", NEW_USER.substitute(wallet=str(wallet)))
            console.log(WALLET_CREATED.substitute(user=name,
                                                  public_key=wallet.public_key))

        self.wallet = wallet
        self.wallet.save(name)


    def send(self, other_user: "User", amount: float, note: str, event, anonymous: bool = False) -> Transaction:
        """
        """
        transaction = TipTransaction(self, other_user, amount, note, event, anonymous)
        return transaction.send()

    def withdraw(self, amount: float, address: str, note: str, event) -> Transaction:
        """

        """
        transaction = WithdrawTransaction(self, address, amount, note, event)
        return transaction.send()

    def message(self, subject: str, message: str) -> None:
        """
        Messages the user on Reddit

        Arguments:
            subject (str):
            message (str):
        """
        reddit.redditor(self.name).message(subject, message)
