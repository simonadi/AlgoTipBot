"""
File containing message templates
"""

from string import Template

from algotip_bot.clients import NETWORK

ALGOEXPLORER_LINK = f"https://{'testnet.' if NETWORK == 'testnet' else ''}algoexplorer.io"

TRANSACTION_CONFIRMATION = Template("Your tip to $receiver for $amount Algos was successfuly sent \n\n"
                                    f"You can check the transaction [here]({ALGOEXPLORER_LINK}/tx/$transaction_id)")

WALLET_REPR = Template(f"Public key : [$public_key]({ALGOEXPLORER_LINK}/address/$public_key) "
                       "[(QR Code)]($qr_code_link) \n\n"
                       "Private key : $private_key \n\n"
                       "Balance : $balance Algos")

WALLET_CREATED = Template("Wallet created for user $user \n"
                          "Public key : $public_key")

EVENT_RECEIVED = Template("Received a new $event_type #$command_id from $author\n"
                          "Event body : $body")

TIP_RECEIVED = Template("$sender tipped you $amount Algos\n\n")

NEW_USER = Template("Welcome, since you are a new user I created you a wallet. Here's the wallet information :\n\n"
                    "$wallet \n\n"
                    "**Recommendations** : keep the lowest amount of ALGOs possible in this wallet by withdrawing "
                    "the funds to a personal wallet, "
                    "because by keeping ALGOs in the bot's wallets you're entrusting the person "
                    "who runs the bot (/u/redswoosh) with these funds")

WITHDRAWAL_CONFIRMATION = Template("Withdrawal of $amount Algos to address $address successful \n\n"
                                   f"You can check the transaction [here]({ALGOEXPLORER_LINK}/tx/$transaction_id)")

NO_WALLET = ("You do not have an account yet. To open one, click on this "
             "[link](https://www.reddit.com/message/compose/?to=AlgorandTipBot&subject=NewAccount&message=wallet)"
             " and send the message")

INVALID_COMMAND = ("Sorry, I didn't understand what you were trying to do. \n\n"
                   "You can see a list of available commands "
                   "[here](https://github.com/simonadi/AlgoTipBot)")

INSUFFICIENT_FUNDS = Template("You tried to take $amount Algos out of your wallet"
                              " but you currently do not have enough funds to do this "
                              "transaction.\n\n"
                              "You can use `wallet` to get your address and fund your account\n\n"
                              "**Note :** the wallet needs to have 0.1 Algos to be active. "
                              "You can still withdraw it by using `withdraw all <address>`")

USER_NOT_FOUND = Template("Hey, I see that you tried to tip `$username`, "
                          "but I can't find a redditor with that username.")

SUBREDDIT_NOT_FOUND = Template("I'm sorry but I couldn't find the subreddit `$subreddit`.")

NOT_MODERATOR = ("Hello, it looks like you tried to perform an action that is only accessible "
                 "to the moderators of the subreddit")

ZERO_TRANSACTION = ("I cancelled your transaction because you tried to do a transaction"
                    " of less than 1e-6 Algos, which is the smallest fraction "
                    "of Algos. This transaction would send 0 Algos and make you lose the fee.")

LIST_SUBREDDITS = Template("I am currently active on these subreddits : $subreddits \n\n"
                           "It means that you can use the `!atip` command on these specific subreddits")
