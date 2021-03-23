from rich.console import Console
import praw

from praw.models.reddit.message import Message
from praw.models.reddit.comment import Comment

from handlers import handle_comment, handle_message

console = Console()

def main():
    """

    """
    client = praw.Reddit(
            "AlgorandTipBot",
            user_agent="AlgoTipBot"
    )

    for event in client.inbox.stream():
        if isinstance(event, Message):
            handle_message(event)
        elif isinstance(event, Comment):
            handle_comment(event)
        else:
            console.log(f"Unknown event was received, of type : {type(event)}")

        client.inbox.mark_read([event])


if __name__ == "__main__":
    main()
    # Put an option to choose the network I wanna connect to (mainnet or testnet)