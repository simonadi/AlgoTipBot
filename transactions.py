from abc import ABC

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
                                    self.destination,
                                    self.amount,
                                    note=self.message,
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
        last_round = client.status().get('last-round')
        txinfo = client.pending_transaction_info(txid)
        return (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0)

    def save(self):
        """

        """
        redis.incr("tx_id")
        redis_tx_id = redis.get("tx_id")
        redis.hset(f"algotip-withdrawals:{redis_tx_id}", {"user": self.sender.name,
                                                          "amount": self.amount,
                                                          "transaction_id": self.tx_id,
                                                          "fee": self.fee,
                                                          "time": self.time})