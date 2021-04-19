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
from rich.console import Console

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

CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
CLIENT_ID = os.environ.get("CLIENT_ID")
PASSWORD = os.environ.get("PASSWORD")
USERNAME = os.environ.get("USERNAME")
USER_AGENT = os.environ.get("USER_AGENT")

# Fetches information from the praw.ini file
reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            password=PASSWORD,
            username=USERNAME,
            user_agent=USER_AGENT
)

######################### Initialize Rich console #########################

console = Console()
