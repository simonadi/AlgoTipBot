from praw.models.reddit.message import Message
from praw.models.reddit.comment import Comment

def handle_comment(comment: Comment) -> None:
    """

    """
    print("It's a comment : ")
    print(comment.body)

def handle_message(message: Message) -> None:
    """
    """
    print("It's a message :")
    print(message.body)