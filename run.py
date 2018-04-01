# coding=utf-8
from slackbot.bot import Bot
from slackbot.bot import respond_to
import re
import tweepy
import os

@respond_to('searchTweet (.*)')
def search_tweet(message, word):
    message.send('CONSUMER_KEYとか探す...')
    # twitterのアクセス情報
    auth = tweepy.OAuthHandler(os.environ.get(CONSUMER_KEY), os.environ.get(CONSUMER_SECRET))
    auth.set_access_token(os.environ.get(ACCESS_TOKEN), os.environ.get(ACCESS_TOKEN_SECRET))
    api = tweepy.API(auth)
    global post_text
    message.send(word + 'でtweet検索するね...')
    search_results = api.search(q=word, lang='ja', result_type='recent', count=3)
    for result in search_results:
        message.send('tweet検索結果見つかったからまとめる...')
        user_name_formatted = result.user.name + "@(" + result.user.screen_name + ")"
        text = result.text
        post_text = post_text + user_name_formatted + "\n" + text + "\n\n"
    message.send('こんなツイート見つかりましたわ。\n' + post_text)


def main():
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
