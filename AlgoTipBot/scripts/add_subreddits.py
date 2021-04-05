from AlgoTipBot.clients import redis

redis.sadd("subreddits", *{"cryptocurrency", "algorand", "algorandofficial", "bottesting"})
