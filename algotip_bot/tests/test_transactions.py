import os

import pytest

from time import sleep

from algotip_bot.clients import algod
from algotip_bot.errors import InsufficientFundsError, ZeroTransactionError
from algotip_bot.instances import User, Wallet
from algotip_bot.tests.utils import reset_balances
from algotip_bot.utils import wait_for_confirmation

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

    sleep(5)

def test_small_tip(users):
    user1, user2 = users
    transaction = user1.send(user2, 1, "", None)
    wait_for_confirmation(transaction.tx_id, 10)
    assert user2.wallet.balance == 1.1

def test_zero_tip(users):
    user1, user2 = users
    with pytest.raises(ZeroTransactionError):
        transaction = user1.send(user2, 1e-8, "", None)

@pytest.mark.skip(reason="Confirmation for big transactions not implemented yet")
def test_tip_above_ten(users):
    user1, user2 = users
    transaction = user1.send(user2, 12, "", None)
    pass

def test_insufficient_funds_tip(users):
    user1, user2 = users
    with pytest.raises(InsufficientFundsError):
        transaction = user2.send(user1, 0.5, "", None)

def test_withdraw(users):
    user1, user2 = users
    transaction = user1.withdraw(1, WALLET2_PUBLIC_KEY, "", None)
    wait_for_confirmation(transaction.tx_id, 10)
    assert user2.wallet.balance == 1.1

def test_insufficient_funds_withdraw(users):
    user1, user2 = users
    with pytest.raises(InsufficientFundsError):
        user2.withdraw(1, WALLET1_PUBLIC_KEY, "", None)

def test_zero_withdraw(users):
    user1, user2 = users
    with pytest.raises(ZeroTransactionError):
        user1.withdraw(1e-8, WALLET2_PUBLIC_KEY, "", None)
