from rich.console import Console

from time import time, sleep

from handlers import EventHandler, InvalidCommandError

from transactions import TipTransaction, WithdrawTransaction
from instances import reddit
import traceback
from templates import TRANSACTION_CONFIRMATION, TIP_RECEIVED, NEW_USER, WITHDRAWAL_CONFIRMATION, INVALID_COMMAND

console = Console()

event_handler = EventHandler()

def main():
    """
    Function running the main loop of the bot
    """
    waiting = 0

    while True:
        if not waiting:
            for transaction in event_handler.unconfirmed_transactions.copy():
                if transaction.confirmed():
                    console.log(f'Transaction {transaction.tx_id} confirmed')


                    if isinstance(transaction, TipTransaction):
                        transaction.trigger_event.reply(TRANSACTION_CONFIRMATION.substitute(amount=transaction.amount,
                                                                                            receiver=transaction.receiver.name))

                        reddit.redditor(transaction.receiver.name).message(
                            subject="AlgoTip",
                            message=TIP_RECEIVED.substitute(sender=transaction.sender.name if not transaction.anonymous else "An anonymous redditor",
                                                            amount=transaction.amount)
                        )

                    elif isinstance(transaction, WithdrawTransaction):
                        transaction.trigger_event.reply(WITHDRAWAL_CONFIRMATION.substitute(amount=transaction.amount,
                                                                                          address=transaction.destination))

                    event_handler.unconfirmed_transactions.remove(transaction)
                    transaction.save()

        for event in reddit.inbox.unread():
            try:
                new_transaction = event_handler.handle_event(event)
                reddit.inbox.mark_read([event])

                if new_transaction is not None:
                    unconfirmed_transactions.add(new_transaction)

            except InvalidCommandError:
                event.reply(INVALID_COMMAND)
            except Exception as e:
                event.author.message("Issue", "Hello, I'm sorry but an unknown issue occured when handling\n\n "
                                              f"***{event.body}*** \n\n Please contact u/RedSwoosh to have it resolved")
                console.log("An unknown issue occured")
                traceback.print_exc()
                exit()

        waiting = (waiting + 1) % 10 # To check the transctions every 10 iterations to not spam the Algo API

        sleep(0.1)


if __name__ == "__main__":
    main()
    # Put an option to choose the network I wanna connect to (mainnet or testnet)
