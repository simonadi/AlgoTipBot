# pylint: disable=C0321

"""
File containing the EventHandler class, that takes in
a praw Event and performs the matching action
"""

from time import time_ns
from typing import Union

from algosdk import encoding

from praw.models.reddit.comment import Comment
from praw.models.reddit.message import Message

from algotip_bot.clients import console, redis
from algotip_bot.errors import (InsufficientFundsError, InvalidCommandError,
                               InvalidSubredditError, InvalidUserError,
                               NotModeratorError, ZeroTransactionError)
from algotip_bot.instances import User
from algotip_bot.templates import (EVENT_RECEIVED, INSUFFICIENT_FUNDS,
                                  NO_WALLET, ZERO_TRANSACTION, LIST_SUBREDDITS)
from algotip_bot.utils import is_float, valid_subreddit, valid_user


class EventHandler:
    """
    Class used to handle an incoming event
    and keep in memory the unconfirmed transactions
    note: could probably do  without a class
    """
    unconfirmed_transactions: set = set()

    def handle_comment(self, comment: Comment) -> None:
        """
        Handle a comment.
        The only use of the comment is to tip the person whose
        post/comment was commented using !atip
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
            transaction = author.send(receiver, amount, note)
            self.unconfirmed_transactions.add(transaction)
        except ZeroTransactionError:
            author.message("Zero transaction",
                           ZERO_TRANSACTION)
        except InsufficientFundsError as e: # pylint: disable=C0103
            author.message("Insufficient funds",
                           INSUFFICIENT_FUNDS.substitute(balance=e.balance,
                                                         amount=e.amount))
    def handle_message(self, message: Message) -> None: # pylint: disable=R0912, R0915
        """
        Parses the incoming message to determine what action to take
        The user can:
         * tip (anonymously)
         * withdraw
         * check balance
         * (de)activate the bot on subreddits
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
                transaction = author.send(receiver, amount, note, anonymous)
                self.unconfirmed_transactions.add(transaction)
            except ZeroTransactionError:
                author.message("Zero transaction",
                               ZERO_TRANSACTION)
            except InsufficientFundsError as e: # pylint: disable=C0103
                author.message("Insufficient funds",
                               INSUFFICIENT_FUNDS.substitute(balance=e.balance,
                                                             amount=e.amount))

        ######################### Handle withdraw command #########################
        elif main_cmd == "withdraw":
            if len(command) < 2: raise InvalidCommandError(message.body)
            if not ((amount:=command.pop(0)) or is_float(amount)): raise InvalidCommandError(message.body)
            if not encoding.is_valid_address(address:=command.pop(0)): raise InvalidCommandError(message)
            note = " ".join(command)

            try:
                transaction = author.withdraw(amount, address, note)
                self.unconfirmed_transactions.add(transaction)
            except ZeroTransactionError:
                author.message("Zero transaction",
                               ZERO_TRANSACTION)
            except InsufficientFundsError as e: # pylint: disable=C0103
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
            if (action:=command.pop(0)) not in ("add", "remove", "list"): raise InvalidCommandError(message.body)

            if action == "list":
                author.message('Subreddits',
                               LIST_SUBREDDITS.substitute(subreddits=', '.join(redis.smembers('subreddits'))))
                return

            if not valid_subreddit(subreddit:=(command.pop(0).lower())): raise InvalidSubredditError(subreddit)
            if not author.is_moderator(subreddit): raise NotModeratorError

            if action == "add":
                redis.sadd("subreddits", subreddit)
                console.log(f"Subreddit {subreddit} added")
                author.message('Subreddit added', f'The subreddit {subreddit} was sucessfully added')
            elif action == "remove":
                redis.srem("subreddits", subreddit)
                console.log(f"Subreddit {subreddit} removed")
                author.message('Subreddit removed', f'The subreddit {subreddit} was sucessfully removed')


        ######################### Handle unknown command #########################
        else:
            raise InvalidCommandError(message.body)

    def handle_event(self, event: Union[Comment, Message]) -> None:
        """
        Logs the incoming event and distributes it to handle_comment
        or handle_message depending on the type
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
