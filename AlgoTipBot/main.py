"""
File containing the main loop
"""

import traceback
from time import sleep

from instances import reddit

from AlgoTipBot.clients import console
from AlgoTipBot.errors import InvalidUserError
from AlgoTipBot.handlers import EventHandler
from AlgoTipBot.templates import INVALID_COMMAND
from AlgoTipBot.templates import TIP_RECEIVED
from AlgoTipBot.templates import TRANSACTION_CONFIRMATION
from AlgoTipBot.templates import WITHDRAWAL_CONFIRMATION
from AlgoTipBot.transactions import TipTransaction
from AlgoTipBot.transactions import WithdrawTransaction
from AlgoTipBot.utils import stream

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
                    transaction.send_confirmation()
                    transaction.log()
                    event_handler.unconfirmed_transactions.remove(transaction)

        for event in stream():
            try:
                event_handler.handle_event(event)
            except InvalidCommandError:
                event.author.message("Invalid Command", INVALID_COMMAND)
            except InvalidUserError as e:
                event.author.message("User not found", USER_NOT_FOUND.substitute(username=e.username))
            except Exception: #pylint: disable=W0703
                event.author.message("Issue", "Hello, I'm sorry but an unknown issue occured when handling\n\n "
                                             f"***{event.body}*** \n\n Please contact u/RedSwoosh to have it resolved")
                console.log("An unknown issue occured")
                traceback.print_exc()
            reddit.inbox.mark_read([event])

        waiting = (waiting + 1) % 5

        sleep(0.5)

if __name__ == "__main__":
    main()
    # Put an option to choose the network I wanna connect to (mainnet or testnet)
