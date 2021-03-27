<img src="images/logo.png" alt="logo" height="100"/>  <h1>AlgoTipBot</h1>


**AlgoTipBot** is a service that allows redditors to tip each other with [Algos](https://www.algorand.com/). It is running through the reddit user [/u/AlgorandTipBot](https://www.reddit.com/user/AlgorandTipBot).

## Get started

If you plan on using this service to tip, you'll first have to setup your wallet. 

In order to do this, just click this [link](https://www.reddit.com/message/compose/?to=AlgorandTipBot&subject=NewAccount&message=wallet) and send the message. /u/AlgorandTipBot will send you a message with your public key (wallet address) and your mnemonic sentence. 

Please not these down, to make sure that you can recover your wallet. You can ask for the public/private key pair at any moment by sending `wallet` to /u/AlgorandTipBot in PM.

Once you have your wallet address, fund your account, and check the balance using `walllet` to make sure that you received your Algos.

You're now ready to tip !

## Commands

### Private messages

When [sending a PM](https://www.reddit.com/message/compose/?to=AlgorandTipBot) to /u/AlgorandTipBot, you can use these three commands : 

 - `wallet` : /u/AgorandTipBot will send you back a message containing your wallet information i.e. your keys and your current balance
 - `tip <amount> <user> <note>` \
    `amount` has to be a floating point number\
    `user` has to be a valid Reddit username\
    `note` will be everything left in  the message\
    **Note** : by default, the user that you tip will be sent a message saying that you tipped him. If you don't want him to know your name, you can set the PM subject as `anonymous`
 - `withdraw <amount> <address> <note>` \
    `amount` has to be a floating point number\
    `address` is an Algorand wallet address (58 characters, either capitalized letter or number)\
    `note` will be everything left in the message

### Comments

At the moment /u/AlgorandTipBot only supports one command through comments, which is used to tip the person who wrote the comment/post that you're commenting. The format is simple : 

`/u/AlgorandTipBot <amount> <note>`
