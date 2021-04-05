from time import time_ns
from typing import Union

from praw.models.reddit.comment import Comment
from praw.models.reddit.message import Message

from AlgoTipBot.clients import console
from AlgoTipBot.clients import redis
from AlgoTipBot.errors import InsufficientFundsError
from AlgoTipBot.errors import InvalidCommandError
from AlgoTipBot.errors import InvalidSubredditError
from AlgoTipBot.errors import NotModeratorError
from AlgoTipBot.errors import ZeroTransactionError
from AlgoTipBot.instances import Transaction
from AlgoTipBot.instances import User
from AlgoTipBot.templates import EVENT_RECEIVED
from AlgoTipBot.templates import INSUFFICIENT_FUNDS
from AlgoTipBot.templates import NEW_USER
from AlgoTipBot.templates import NO_WALLET
from AlgoTipBot.templates import USER_NOT_FOUND
from AlgoTipBot.templates import ZERO_TRANSACTION
from AlgoTipBot.utils import is_float
from AlgoTipBot.utils import valid_subreddit
from AlgoTipBot.utils import valid_user


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
        if first_word not in ("!atip"):
            return

        if not command: raise InvalidCommandError(comment.body) # If command empty after popping username
        if not is_float(amount:=command.pop(0)): raise InvalidCommandError(comment.body)

        amount = float(amount)
        note = " ".join(command)

        try:
            transaction = author.send(receiver, amount, note, comment)
            self.unconfirmed_transactions.add(transaction)
        except ZeroTransactionError:
            author.message("Zero transaction",
                           ZERO_TRANSACTION)
        except InsufficientFundsError as e:
            author.message("Insufficient funds",
                           INSUFFICIENT_FUNDS.substitute(balance=e.balance,
                                                         amount=e.amount))
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
            if len(command) < 2: raise InvalidCommandError(message.body)

            if not is_float(amount:=command.pop(0)): raise InvalidCommandError(message.body)

            if not valid_user(username:=command.pop(0)): raise InvalidUserError(username)

            amount = float(amount)
            receiver = User(username)
            note = " ".join(command)

            try:
                transaction = author.send(receiver, amount, note, message, anonymous)
                self.unconfirmed_transactions.add(transaction)
            except ZeroTransactionError:
                author.message("Zero transaction",
                               ZERO_TRANSACTION)
            except InsufficientFundsError as e:
                author.message("Insufficient funds",
                               INSUFFICIENT_FUNDS.substitute(balance=e.balance,
                                                             amount=e.amount))

        ######################### Handle withdraw command #########################
        elif main_cmd == "withdraw":
            if len(command) < 2: raise InvalidCommandError(message.body)
            if not ((amount:=command.pop(0)) or is_float(amount)): raise InvalidCommandError(message.body)
            address = command.pop(0) # TODO : check that the address is valid
            note = " ".join(command)

            try:
                transaction = author.withdraw(amount, address, note, message)
                self.unconfirmed_transactions.add(transaction)
            except ZeroTransactionError:
                author.message("Zero transaction",
                               ZERO_TRANSACTION)
            except InsufficientFundsError as e:
                author.message("Insufficient funds",
                               INSUFFICIENT_FUNDS.substitute(balance=e.balance,
                                                             amount=e.amount))
        ######################### Handle wallet command #########################
        elif main_cmd == "wallet":
            if len(command) > 0: raise InvalidCommandError(message.body)

            if author.new:
                pass
            else:
                message.reply(str(author.wallet))

            console.log(f"Wallet information sent to {author.name} (#{author.user_id})")

        ######################### Handle subreddit command #########################
        elif main_cmd == "subreddit":
            if len(command) < 2: raise InvalidCommandError(message.body)
            if (action:=command.pop(0)) not in ("add", "remove"): raise InvalidCommandError(message.body)
            if not valid_subreddit(subreddit:=command.pop(0)): raise InvalidSubredditError(subreddit)
            if not author.is_moderator(subreddit): raise NotModeratorError

            if action == "add":
                redis.sadd("subreddits", subreddit)
                console.log(f"Subreddit {subreddit} added")
            elif action == "remove":
                redis.srem("subreddits", subreddit)
                console.log(f"Subreddit {subreddit} removed")

        ######################### Handle unknown command #########################
        else:
            raise InvalidCommandError(message.body)

    def handle_event(self, event: Union[Comment, Message]) -> None:
        """

        """
        command_id = redis.incr("command-id")
        redis.zadd("commands", {command_id: time_ns() * 1e-6})
        redis.hmset(f"command:{command_id}", {"user": event.author.name,
                                              "content": event.body})

        console.log(EVENT_RECEIVED.substitute(author=event.author,
                                              command_id=command_id,
                                              event_type=type(event).__name__.lower(),
                                              body=event.body))

        if isinstance(event, Message):
            self.handle_message(event)
        elif isinstance(event, Comment):
            self.handle_comment(event)
        else:
            console.log(f"Unknown event was received, of type : {type(event)}")
