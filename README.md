[![GitHub Super-Linter](https://github.com/simonadi/AlgoTipBot/workflows/Lint%20Code%20Base/badge.svg)](https://github.com/marketplace/actions/super-linter)
[![Python Testing](https://github.com/simonadi/AlgoTipBot/actions/workflows/python-testing.yml/badge.svg?branch=master)](https://github.com/simonadi/AlgoTipBot/actions/workflows/python-testing.yml)

<img src="images/logo.png" alt="logo" height="100"/>  <h1>AlgoTipBot</h1>


**AlgoTipBot** is a service that allows redditors to tip each other with [Algos](https://www.algorand.com/). It is running through the reddit user [/u/AlgorandTipBot](https://www.reddit.com/user/AlgorandTipBot).

## Recommendation

Do not keep Algos for too long in the wallet by withdrawing them to your personal wallet, since leaving any funds in the bot's wallets is also entrusting me with these funds.

## Get started

If you plan on using this service to tip, you'll first have to setup your wallet.

In order to do this, just click this [link](https://www.reddit.com/message/compose/?to=AlgorandTipBot&subject=NewAccount&message=wallet) and send the message. /u/AlgorandTipBot will send you a message with your public key (wallet address) and your mnemonic sentence.

Please note these down, to make sure that you can recover your wallet. (the bot will show them to you again everytime you send `wallet`)

Once you have your wallet address, fund your account, and check the balance using `walllet` to make sure that you received your Algos.

You're now ready to tip !

## Commands

### Private messages

When [sending a PM](https://www.reddit.com/message/compose/?to=AlgorandTipBot) to /u/AlgorandTipBot, you have access to four main commands :

 - `wallet` : /u/AgorandTipBot will send you back a message containing your wallet information i.e. your keys and your current balance
 - `tip` : this has to be followed by the amount and the receiver's username (capitalization doesn't matter). After this you can add any text, it should be added to the transaction note\
   This tip can also be made anonymous by setting `anonymous` as the PM subject.\
   Example : `tip 1 algorandtipbot`
 - `withdraw` : this command is followed by the amount and the Algorand address to which you want to withdraw. The amount can either be a number, or `all` to withdraw everything.\
   Examples : `withdraw 1.2 Y76M3MSY6DKBRHBL7C3NNDXGS5IIMQVQVUAB6MP4XEMMGVF2QWNPL226CA`\
              `withdraw all Y76M3MSY6DKBRHBL7C3NNDXGS5IIMQVQVUAB6MP4XEMMGVF2QWNPL226CA`
 - `subreddit` : this command has 3 available switches :
  - `list` : shows you a list of subreddits that the bot is currently watching (I'll explain in the next section what I mean)
  - `add` followed by a subreddit name (don't include the r/ the bot doesn't like it). You need to be a moderator of the subreddit for this to work. This tells the bot to start watching this subreddit
  - `remove` followed by a subreddit name. Same rules as above. This tells the bot to stop watching the subreddit

### Comments

There is only one functionality available through the comments : tipping. You can do that by
writing `!atip 1` in your comment (replace the `1` with the amount of Algos you want to tip)

This tipping part must be at the beginning of your comment (for now), and can be followed by any text.

This tipping command only works on the subreddits that the bot is watching, that you can get with `subreddit list`.
