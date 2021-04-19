import os

from algosdk.util import microalgos_to_algos

from algotip_bot.clients import algod
from algotip_bot.instances import User, Wallet

WALLET1_PRIVATE_KEY = os.environ["WALLET1_PRIVATE_KEY"]
WALLET1_PUBLIC_KEY = os.environ["WALLET1_PUBLIC_KEY"]
WALLET2_PRIVATE_KEY = os.environ["WALLET2_PRIVATE_KEY"]
WALLET2_PUBLIC_KEY = os.environ["WALLET2_PUBLIC_KEY"]

def reset_balances(user1, user2):
    fee = float(microalgos_to_algos(algod.suggested_params().min_fee))

    to_transfer = user2.wallet.balance - 0.1 - fee

    if to_transfer > 0:
        transaction = user2.send(user1, to_transfer, "", None)
        return transaction
    else:
        return None
