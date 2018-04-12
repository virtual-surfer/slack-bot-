# coding=utf-8
from slackbot.bot import Bot
from template import slackbot_template
from service import batch


def main():
    bot = Bot()
    bot.run()


if __name__ == '__main__':
    main()
