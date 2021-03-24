from rich.console import Console
import praw

from time import time, sleep

from praw.models.reddit.message import Message
from praw.models.reddit.comment import Comment

from handlers import handle_comment, handle_message

from instances import client

console = Console()

def main():
    """
    Function running the main loop of the bot
    """
    unconfirmed_transactions = set()
    waiting = 0

    while True:
        if not waiting:
            for transaction in unconfirmed_transactions:
                if transaction.confirmed():
                    transaction.trigger_event.reply(TRANSACTION_CONFIRMATION.substitute(amount=transaction.amount,
                                                                                        receiver=transaction.receiver.name))
                    unconfirmed_transactions.remove(transaction)
                    transaction.save()

        for event in client.inbox.unread():
            try:
                new_transaction = handle_event(event)
                client.inbox.mark_read([event])

                if new_transaction is not None:
                    unconfirmed_transactions.add(new_transaction)

            except Exception as e:
                console.log(e)

        waiting = (waiting + 1) % 10 # To check the transctions every 10 iterations

        sleep(0.1)
            # Send message to say that an error occured, and to contact me

        # Only put event as read once transaction is confirmed if it is for a transaction
        # That way the event can be answered to easily
        # Transaction checking cannot be done if i use event in stream.
        # Can use while True with .all()

        


if __name__ == "__main__":
    main()
    # Put an option to choose the network I wanna connect to (mainnet or testnet)