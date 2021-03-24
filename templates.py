from string import Template

TRANSACTION_CONFIRMATION = Template("Tipped $receiver for $amount Algos")

WALLET_REPR = Template("Public key : $public_key\n"
                       "Private key : $private_key\n"
                       "Balance : $balance Algos\n")