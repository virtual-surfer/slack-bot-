from slackbot.bot import Bot
from slackbot.bot import respond_to
from slackbot.bot import listen_to
import re
from datetime import datetime

@respond_to('今何時?')
def now(message):
    strftime = datetime.now().strftime("%Y/%m/%d %H時%M分%S秒っすね")
    message.reply(strftime)

@respond_to('hi', re.IGNORECASE)
def hi(message):
    message.reply('I can understand hi or HI!')
    # react with thumb up emoji
    message.react('+1')

@listen_to('Can someone help me?')
def help(message):
    # Message is replied to the sender (prefixed with @user)
    message.reply('Yes, I can!')

    # Message is sent on the channel
    message.send('I can help everybody!')

    # Start a thread on the original message
    message.reply("Here's a threaded reply", in_thread=True)

def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()