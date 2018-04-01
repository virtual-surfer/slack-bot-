from slackbot.bot import respond_to

def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()

@respond_to('今何時？')
def today(message):
    message.reply('a')