Title : AlgorandTipBot Testing

Hey everyone, there was recently a [discussion](https://www.reddit.com/r/AlgorandOfficial/comments/malpyg/algo_tipbot_would_it_be_possible) about building a tipping bot for Algorand, and I said I could potentially work on it.

Well, here it is, I present to you /u/AlgorandTipBot. I built the main functionalities, and I now need your help to stress-test the shit out of it. I'll be running it for the rest of the weekend on the Testnet since I'm currently available to fix whatever comes up (I'll make a post once I take it offline). Depending on the outcome of this I'll see if it is reliable enough to be used on the Mainnet in the following days.

I'd really appreciate if you could try using it a bit for this time, since the more users the more bugs are potentially found. I'll be sending 0.5 (Mainnet) Algos to whoever finds a new bug, so I'm hoping I did a decent job. If you're willing to try it, here are instructions on how to set it up, get some free Testnet Algos, and the available commands :

## Get started

To create a wallet for the service, just click on this [link](https://www.reddit.com/message/compose/?to=AlgorandTipBot&subject=NewAccount&message=wallet) and send the message. /u/AlgorandTipBot will send you a PM with your wallet information. Please not these down to be able to recover your wallet.

To fund this wallet, head to the [testnet faucet](https://bank.testnet.algorand.network/), paste the address that /u/AlgorandTipBot sent you, complete the Captcha, and voilà, you're rich.

## Commands

### Private messages

When [sending a PM](https://www.reddit.com/message/compose/?to=AlgorandTipBot) to /u/AlgorandTipBot, you can use these three commands :

 - `wallet` : /u/AgorandTipBot will send you back a message containing your wallet information i.e. your keys and your current balance
 - `tip <amount> <user> <note>`
    `amount` has to be a floating point number
    `user` has to be a valid Reddit username
    `note` will be everything left in  the message
    **Note** : by default, the user that you tip will be sent a message saying that you tipped him. If you don't want him to know your name, you can set the PM subject as `anonymous`
 - `withdraw <amount> <address> <note>`
    `amount` has to be a floating point number
    `address` is an Algorand wallet address (58 characters, either capitalized letter or number)
    `note` will be everything left in the message

### Comments

At the moment /u/AlgorandTipBot only supports one command through comments, which is used to tip the person who wrote the comment/post that you're commenting. The format is simple :

`/u/AlgorandTipBot <amount> <note>`

## Code

You can find the source code there : https://github.com/simonadi/AlgoTipBot
I'll add more documentation to it and clean it up a bit more in the following days.

## Contact

If you have any suggestions on changes/new features to implement, found a bug, or simply have a question, feel free to send me a PM and we can discuss it.
