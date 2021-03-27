from string import Template

TRANSACTION_CONFIRMATION = Template("Your tip to $receiver for $amount Algos was successfuly sent")

WALLET_REPR = Template("Public key : $public_key \n\n"
                       "Private key : $private_key \n\n"
                       "Balance : $balance Algos \n\n"
                       "[(QR Code)]($qr_code_link)")

WALLET_CREATED = Template("Wallet created for user $user \n"
                          "Public key : $public_key")

EVENT_RECEIVED = Template("Received a new $event_type from $author \n"
                          "Content : $message")

TIP_RECEIVED = Template("$sender tipped you $amount Algos\n\n")

NEW_USER = Template("Welcome, since you are a new user I created you a wallet. Here's the wallet information : \n\n"
                    "$wallet")

WITHDRAWAL_CONFIRMATION = Template("Withdrawal of $amount Algos to address $address successful")

NO_WALLET = ("You do not have an account yet. To open one, click on this "
             "[link](https://www.reddit.com/message/compose/?to=AlgorandTipBot&subject=NewAccount&message=wallet)"
             " and send the message")

INVALID_COMMAND = ("Sorry, I didn't understand what you were trying to do. "
                   "You can see a list of available commands "
                   "[here](https://github.com/simonadi/AlgoTipBot)")

INSUFFICIENT_FUNDS = Template("You tried to take $amount Algos out of your wallet"
                              " but you currently do not have enough funds to do this "
                              "transaction.\n\n"
                              "You can use `wallet` to get your address and fund your account")
