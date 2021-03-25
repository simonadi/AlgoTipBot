from praw.models.reddit.message import Message
from praw.models.reddit.comment import Comment

from instances import Transaction, User
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
        if main_cmd == "tip":
            pass
        elif main_cmd == "withdraw":
            pass
        elif main_cmd == "wallet":
            if len(command) > 1:
                self.help()
            else:
                message.reply(str(author.wallet))
        else:
            self.help()

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
