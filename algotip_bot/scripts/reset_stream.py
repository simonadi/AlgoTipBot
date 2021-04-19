from algotip_bot.clients import reddit, redis
from algotip_bot.utils import COMMENT_COMMANDS

inbox_events = list(reddit.inbox.unread())
reddit.inbox.mark_read(inbox_events)

subreddits = redis.smembers("subreddits")


subrredits_comments = set(reddit.subreddit("+".join(subreddits)).comments(limit=500))
subrredits_comments = {comment for comment in subrredits_comments if any(command in comment.body for command in COMMENT_COMMANDS)}

if subrredits_comments:
    redis.sadd("comment-cache", *{comment.id for comment in subrredits_comments})
