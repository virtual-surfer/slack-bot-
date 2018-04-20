# coding=utf-8
from slackbot.bot import default_reply
from slackbot.bot import respond_to
from slackbot.bot import listen_to
from service import slackbot_service
from service.twitter import twitter_service


@respond_to('coinScreenD')
def coingecko_screenshot_dashboard(message):
    slackbot_service.coingecko_screenshot_dashboard(message)


@respond_to('searchTweet (.*)')
def post_top_tweet(message, word):
    slackbot_service.post_top_tweet(message, word)


@respond_to('tweet (.*) (.*)')
def search_popular_tweet_and_retweet(message, user_screen_name, query):
    twitter_service.search_unpopular_tweet_and_tweet(user_screen_name, query)


@respond_to('reTweet (.*) (.*)')
def search_popular_tweet_and_retweet(message, user_screen_name, query):
    twitter_service.search_popular_tweet_and_retweet(user_screen_name, query)


@respond_to('addTwitterUser (.*)')
def collect_user_tweet(message, user_screen_name):
    """
    指定したTwitterユーザーをDB登録する
    :param message: slackで受け取ったメンション
    :param user_screen_name: TwitterユーザーのアカウントID
    """
    twitter_service.search_insert_user(user_screen_name)


@respond_to('searchFollow (.*) (.*) (.*)')
def search_follow(message, user_screen_name, query, max_count):
    """
    指定したuser_screen_nameのユーザーで、queryで検索したツイッターユーザーをmax_count数フォローして、DBにフォローデータを登録する。
    """
    twitter_service.search_follow(user_screen_name, query, max_count)


@respond_to('unFollow (.*) (.*)')
def unfollow(message, user_screen_name, max_count):
    """
    指定したuser_screen_nameのユーザーで、max_count数のフォローを外して、DBのフォローデータを更新する。
    """
    twitter_service.unfollow(user_screen_name, max_count)


@respond_to('collectTweet (.*) (.*)')
def collect_user_tweet(message, user_screen_name, target_screen_name):
    """
    指定したuser_screen_nameのTwitterユーザーで、target_screen_nameの過去のツイートを最大2000件DB登録する
    :param message: slackで受け取ったメンション
    :param user_screen_name: TwitterユーザーのアカウントID
    """
    twitter_service.collect_user_tweets(user_screen_name, target_screen_name)


@respond_to('collectTweetDiff (.*) (.*)')
def collect_user_tweet(message, user_screen_name, target_screen_name):
    """
    指定したTwitterユーザーのDBにある最新のツイートから新しい順に最大2000件DB登録する
    :param user_screen_name: 起点となるTwitterユーザーのアカウントID
    :param target_screen_name: 対象となるユーザーのアカウントID
    :param message: slackで受け取ったメンション
    """
    twitter_service.collect_user_tweets_diff(user_screen_name, target_screen_name)


@listen_to('(@.+) (.*)')
def dialogue_with_twitter_user(message, user_screen_name, text):
    twitter_service.dialogue_with_twitter_user(message, user_screen_name, text)


@default_reply(matchstr='(.*)')
def talk(message, input):
    slackbot_service.dialogue_with_docomo_api(message, input)
