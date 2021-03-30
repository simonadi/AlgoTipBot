from AlgoTipBot.instances import User, Wallet
from AlgoTipBot.utils import wait_for_confirmation
from AlgoTipBot.clients import algod

from AlgoTipBot.tests.utils import reset_balances

import pytest
import os

WALLET1_PRIVATE_KEY = os.environ["WALLET1_PRIVATE_KEY"]
WALLET1_PUBLIC_KEY = os.environ["WALLET1_PUBLIC_KEY"]
WALLET2_PRIVATE_KEY = os.environ["WALLET2_PRIVATE_KEY"]
WALLET2_PUBLIC_KEY = os.environ["WALLET2_PUBLIC_KEY"]


@pytest.fixture
def users():
    wallet1 = Wallet(WALLET1_PRIVATE_KEY, WALLET1_PUBLIC_KEY)
    user1 = User("user1", wallet1)

    wallet2 = Wallet(WALLET2_PRIVATE_KEY, WALLET2_PUBLIC_KEY)
    user2 = User("user2", wallet2)

    transaction = reset_balances(user1, user2)
    if transaction is not None:
        wait_for_confirmation(transaction.tx_id, 10)

    yield user1, user2

    transaction = reset_balances(user1, user2)
    if transaction is not None:
        wait_for_confirmation(transaction.tx_id, 10)

def test_small_tip(users):
    user1, user2 = users
    transaction = user1.send(user2, 1, "", None)
    wait_for_confirmation(transaction.tx_id, 10)
    assert user2.wallet.balance == 1.1

def test_zero_tip(users):
    user1, user2 = users
    transaction = user1.send(user2, 1e-8, "", None)
    assert transaction is None

def test_tip_above_ten(users):
    user1, user2 = users
    # transaction = user1.send(user2, 12, "", None)
    pass
