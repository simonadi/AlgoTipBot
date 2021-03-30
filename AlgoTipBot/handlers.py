from typing import Union

from clients import redis
from instances import User
from praw.models.reddit.comment import Comment
from praw.models.reddit.message import Message
from rich.console import Console
from templates import EVENT_RECEIVED, NEW_USER, USER_NOT_FOUND, NO_WALLET
from transactions import Transaction
from utils import is_float, valid_user

console = Console()

class EventHandler:
    unconfirmed_transactions: set = set()

    def handle_comment(self, comment: Comment) -> None:
        """

        """
        author = User(comment.author.name)
        if author.new:
            comment.reply(NO_WALLET)
            return
        receiver = User(comment.parent().author.name)
        command = comment.body.split()
        first_word = command.pop(0).lower() # Get rid of the /u/AlgorandTipBot
        if first_word not in ("/u/algorandtipbot", "u/algorandtipbot", "!atip"):
            return

        if not command: raise InvalidCommandError # If command empty after popping username
        if not is_float(amount:=command.pop(0)): raise InvalidCommandError

        amount = float(amount)
        note = " ".join(command)

        transaction = author.send(receiver, amount, note, comment)
        if transaction is not None: self.unconfirmed_transactions.add(transaction)

    def handle_message(self, message: Message) -> None:
        """
        Parses the incoming message to determine what action to take
        """
        author = User(message.author.name)
        command = message.body.split()
        main_cmd = command.pop(0).lower()
        anonymous = (message.subject.lower() == "anonymous")

        ######################### Handle tip command #########################
        if main_cmd == "tip": # This whole check is ugly, make it nice
            if len(command) < 2: raise InvalidCommandError

            if not is_float(amount:=command.pop(0)): raise InvalidCommandError

            if not valid_user(username:=command.pop(0)):
                message.reply(USER_NOT_FOUND.substitute(username=username))
                return

            amount = float(amount)
            receiver = User(username)
            note = " ".join(command)

            transaction = author.send(receiver, amount, note, message, anonymous)
            if transaction is not None: self.unconfirmed_transactions.add(transaction)

        ######################### Handle withdraw command #########################
        elif main_cmd == "withdraw":
            if len(command) < 2: raise InvalidCommandError
            if not ((amount:=command.pop(0)) or is_float(amount)): raise InvalidCommandError
            address = command.pop(0) # TODO : check that the address is valid
            note = " ".join(command)

            transaction = author.withdraw(amount, address, note, message)
            if transaction is not None: self.unconfirmed_transactions.add(transaction)

        ######################### Handle wallet command #########################
        elif main_cmd == "wallet":
            if len(command) > 0: raise InvalidCommandError

            if author.new:
                return
            else:
                message.reply(str(author.wallet))
        ######################### Handle unknown command #########################
        else:
            raise InvalidCommandError

    def handle_event(self, event: Union[Comment, Message]) -> None:
        """

        """
        console.log(EVENT_RECEIVED.substitute(author=event.author,
                                              message=event.body,
                                              event_type=type(event).__name__))

        redis.incr("command_id")
        command_id = redis.get("command_id")
        redis.set(f"commands:{command_id}", event.body)

        if isinstance(event, Message):
            self.handle_message(event)
        elif isinstance(event, Comment):
            self.handle_comment(event)
        else:
            console.log(f"Unknown event was received, of type : {type(event)}")
