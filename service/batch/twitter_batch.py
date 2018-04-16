# coding=utf-8
from service.twitter import twitter_service
from service import slackbot_service
import datetime


def tweet_post_slack(query, type, count, channel):
    """
    与えた文字列(query)でtypeでtwitter検索し、特定のチャンネル(channel)にいいね数がついているもの順にcount数取得してslackに投稿
    type: popular->人気のツイート。recent->最新のツイート。mixed->全てのツイート。
    """
    api = twitter_service.prepare_twitter_api()
    search_results = twitter_service.search_tweet(api, query, type, 100)
    if len(search_results) == 0:
        slackbot_service.send_to_slack(message, 'ツイート見つからなかったす。')
        return

    # いいね数の多い順のつぶやき一覧取得
    statuses = twitter_service.sort_by_favorite_count(search_results, False)
    # いいね数の多いcount数のつぶやき辞書取得
    top_five_statuses_dictionary = twitter_service.select_statuses(statuses, count)
    top_five_statuses = top_five_statuses_dictionary.values()
    # slackにポストする形式に整えた文章作成
    text = twitter_service.create_tweet_list_text(top_five_statuses)
    slackbot_service.post_text(channel, '自動お知らせっすわ！\n{}'.format(text))


def execute():
    # 以下でバッチ処理
    now = datetime.datetime.now()
    current_time = time(now.hour, now.minute, now.second)

    slackbot_service.post_text('general', 'now()で取得した現在時刻:{}'.format(now))

    # 18時~18時5分の間に実行
    if time(18, 0, 0) <= current_time < time(18, 5, 0):
        tweet_post_slack('', 'popular', 5, 'general')
