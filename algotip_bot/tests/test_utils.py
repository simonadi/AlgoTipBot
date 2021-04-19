import pytest

from algotip_bot.utils import is_float, valid_user


def test_valid_user():
    assert valid_user('redswoosh') == True

def test_invalid_user():
    assert valid_user('ifjqfdffq-jrequfbds') == False

def test_valid_float():
    assert is_float('2.3') == True

def test_invalid_float():
    assert is_float('49a') == False
