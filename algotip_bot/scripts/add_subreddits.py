from algotip_bot.clients import redis

redis.sadd("subreddits", *{"cryptocurrency", "algorand", "algorandofficial", "bottesting"})
