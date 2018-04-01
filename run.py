# coding=utf-8
from slackbot.bot import Bot
from slackbot.bot import respond_to
import re
import tweepy

# twitterのアクセス情報
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

@respond_to('searchTweet (.*)')
def search_tweet(message, word):
    global post_text
    search_results = api.search(q=word, lang='ja', result_type='recent', count=3)
    for result in search_results:
        user_name_formatted = result.user.name + "@(" + result.user.screen_name + ")"
        text = result.text
        post_text = post_text + user_name_formatted + "\n" + text + "\n\n"
    message.send('こんなツイート見つかりましたわ。\n' + post_text)

def main():
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
