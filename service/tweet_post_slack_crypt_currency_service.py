# coding=utf-8
import twitter_service
import slackbot_service

prepare_twitter_api()

search_results = twitter_service.search_tweet(api, 'コスプレイヤー', 'recent', 100)
if len(search_results) == 0:
    send_to_slack(message, 'ツイート見つからなかったす。')

# いいね数の多い順のつぶやき一覧取得
statuses = twitter_service.sort_by_favorite_count(search_results, False)
# いいね数の多い5つのつぶやき辞書取得
top_five_statuses_dictionary = twitter_service.select_statuses(statuses, 5)
top_five_statuses = top_five_statuses_dictionary.values()
# slackにポストする形式に整えた文章作成
text = twitter_service.create_tweet_list_text(top_five_statuses)
slackbot_service.post_text('general', text)
