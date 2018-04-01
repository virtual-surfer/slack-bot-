from slackbot.bot import Bot
from datetime import datetime

def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()

@respond_to('今何時？')
def today(message):
    strftime = datetime.now().strftime("%Y/%m/%d %H時%M分%秒っすね")
    message.reply(strftime)