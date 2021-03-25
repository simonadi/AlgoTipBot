from rich.console import Console

from time import time, sleep

from handlers import EventHandler

from instances import client
import traceback

console = Console()

event_handler = EventHandler()

def main():
    """
    Function running the main loop of the bot
    """
    unconfirmed_transactions = set()
    waiting = 0

    while True:
        if not waiting:
            for transaction in event_handler.unconfirmed_transactions:
                if transaction.confirmed():
                    transaction.trigger_event.reply(TRANSACTION_CONFIRMATION.substitute(amount=transaction.amount,
                                                                                        receiver=transaction.receiver.name))
                    unconfirmed_transactions.remove(transaction)
                    transaction.save()

        for event in client.inbox.unread():
            try:
                new_transaction = event_handler.handle_event(event)
                client.inbox.mark_read([event])

                if new_transaction is not None:
                    unconfirmed_transactions.add(new_transaction)

            except Exception as e:
                console.log("An unknown issue occured")
                traceback.print_exc()
                exit()

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
