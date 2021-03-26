from praw.models.reddit.message import Message
from praw.models.reddit.comment import Comment

from instances import User
from transactions import Transaction
from typing import Union

from rich.console import Console

from templates import EVENT_RECEIVED

console = Console()

class EventHandler:
    unconfirmed_transactions: set = set()

    def handle_comment(self, comment: Comment) -> None:
        """

        """
        command = comment.body.split()

    def handle_message(self, message: Message) -> None:
        """
        Parses the incoming message to determine what action to take
        """
        author = User(message.author)
        command = message.body.split()
        anonymous = (message.subject.lower() == "anonymous")
        main_cmd = command[0]
        ######################### Handle tip command #########################
        if main_cmd == "tip": # This whole check is ugly, make it nice
            # if not reddit_user_exists(command[1]):
            #     pass # Tell them the user can't be found
            receiver = User(command[1])
            try:
                amount = float(command[2])
            except:
                self.help(author, command) # Tell them the format is invalid
            message = " ".join(command[3:])
            author.send(receiver, amount, message)
        ######################### Handle withdraw command #########################
        elif main_cmd == "withdraw":
            if len(command) > 4:
                self.help(author)
                return
            elif len(command) < 3:
                self.help(author)
                return
            elif len(command) == 4:
                message = command[3]
            
            amount = command[1]
            address = command[2]
            if amount == "all":
                pass # Withdraw everything and delete wallet from DB
            else:
                try:
                    amount = float(amount)
                except:
                    self.help(author)
                    return
                
        ######################### Handle wallet command #########################
        elif main_cmd == "wallet":
            if len(command) > 1:
                self.help(author)
            else:
                message.reply(str(author.wallet))
        ######################### Handle unknown command #########################
        else:
            self.help(author)

    def handle_event(self, event: Union[Comment, Message]) -> Transaction:
        """

        """
        console.log(EVENT_RECEIVED.substitute(author=event.author,
                                              message=event.body,
                                              event_type=type(event).__name__))
        if isinstance(event, Message):
            self.handle_message(event)
        elif isinstance(event, Comment):
            self.handle_comment(event)
        else:
            console.log(f"Unknown event was received, of type : {type(event)}")

    def help(self) -> None:
        """
        """
        print("Available commands : ")
