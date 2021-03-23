from algosdk.account import generate_account

from dataclasses import dataclass

from redis import Redis

from datetime import datetime

redis_connection = Redis()

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
        private_key, public_key = redis.get_keys() # TODO : define this
        return cls(private_key, public_key)

    def save(self, username: str) -> None:
        """
        Saves the wallet information to the Redis 
        database
        """
        redis.add_wallet(self.private_key, self.public_key, username)

@dataclass
class Transaction:
    sender: User
    receiver: User
    amount: float
    message: str
    tx_id: str = None
    fee: float = None
    time: datetime = None

    def send(self):
        """

        """
        pass

    def check_confirmation(self):
        """

        """
        pass


class User:
    """
    """
    def __init__(self, name: str) -> None:
        """

        """
        # Check if user exists in DB
        # If he doesn't, add him and create him a wallet.
        # Otherwise, load everything
        self.name = name
        if name in redis.users():
            self.wallet = Wallet.load(name)
        else:
            redis.add_user(name)
            self.wallet = Wallet.generate(name)

    def send(self, other_user: "User", amount: float, message: str) -> bool:
        """
        """
        # Send transaction 
        # See what to do about confirmation waiting, because it'd pause the bot for other users.
        # Maybe add the tx_id to a list of transactions to be checked on each iteration
        # If this is added as a Transaction, the username can be fetched from there and a message can be sent
        transaction = Transaction(self, other_user, amount, message)
        confirmation = transaction.confirm()
        if confirmation:
            transaction.send()
        else:
            # Confirm that tip was aborted
            return