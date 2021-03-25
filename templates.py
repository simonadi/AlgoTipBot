from string import Template

TRANSACTION_CONFIRMATION = Template("Tipped $receiver for $amount Algos")

WALLET_REPR = Template("Public key : $public_key \n\n"
                       "Private key : $private_key \n\n"
                       "Balance : $balance Algos \n\n"
                       "[(QR Code)]($qr_code_link)")

WALLET_CREATED = Template("Wallet created for user $user \n"
                          "Public key : $public_key")

EVENT_RECEIVED = Template("Received a new $event_type from $author \n"
                          "Content : $message")
