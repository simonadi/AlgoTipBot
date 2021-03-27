from redis import Redis

from algosdk.v2client import algod

import praw

import os

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

reddit = praw.Reddit(
            "AlgorandTipBot",
            user_agent="AlgoTipBot"
)
