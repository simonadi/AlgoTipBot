"""
File containing all clients to communicate with services
Redis: database running locally
algod: SDK to interact with the Algorand blockchain
Reddit: API wrapper to communicate with reddit
"""

import os

import praw
from algosdk.v2client import algod
from redis import Redis

######################### Initialize Redis connection #########################

# Get the Redis DB password from the environment variables and initialize the client
REDIS_PW = os.environ.get("REDIS_PW")
redis = Redis(password=REDIS_PW, decode_responses=True) # decode_responses is used to automatically
                                                        # convert bytes to strings and vice-versa

######################### Initialize Algod connection #########################

# Get API key from the environment variables and initialize the client
ALGOD_TOKEN = os.environ.get("ALGOD_TOKEN")
NETWORK = os.environ.get("NETWORK")

algod_address = f"https://{NETWORK}-algorand.api.purestake.io/ps2"

headers = {
    "x-api-key": ALGOD_TOKEN
}

algod = algod.AlgodClient(ALGOD_TOKEN, algod_address, headers)


######################### Initialize Reddit connection #########################

# Fetches information from the praw.ini file
reddit = praw.Reddit(
            "AlgorandTipBot",
            user_agent="AlgoTipBot"
)
