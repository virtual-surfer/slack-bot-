# coding=utf-8
import tweepy
import os
from repository import twitter_tweet_repository


def prepare_twitter_api():
    """
    TwitterのAPIアクセスキーを取得
    """
    auth = tweepy.OAuthHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])
    auth.set_access_token(os.environ['ACCESS_TOKEN'], os.environ['ACCESS_TOKEN_SECRET'])
    return tweepy.API(auth)


def search_tweet(api, word, result_type, count):
    """
    Twitterでwordで一致する日本語つぶやき情報を取得
    result_type: popular->人気のツイート。recent->最新のツイート。mixed->全てのツイート。
    """
    search_results = api.search(q=word, lang='ja', result_type=result_type, count=count)
    return search_results


def create_tweet_list_text(statuses):
    """
    与えたつぶやきのリストを元に、以下のようなテキストを作成する
    --------------------------
    太郎(@taro)
    つぶやきだよ
    (2いいね)https://twitter.com/taro/status/randomalphabet
    --------------------------
    ...
    """
    post_text = ''
    for status in statuses:
        user = status.user
        fav_count = status.favorite_count
        tweet_link = 'https://twitter.com/{}/status/{}'.format(user.screen_name, str(status.id))
        result_text = '\n{}@({})\n{}\n({}いいね){}\n'.format(user.name, user.screen_name, status.text, str(fav_count),
                                                          tweet_link)
        post_text = '{}-------------------------------------------------------{}'.format(post_text, result_text)
    return post_text


def sort_by_favorite_count(statuses, is_asc):
    """
    引数で与えられたつぶやきを「いいね」の少ない順で並び替えてstatusリストを返す。(is_ascがfalseなら多い順)
    """
    # 辞書{つぶやき, いいね数}に詰めていく
    if is_asc:
        return sorted(statuses, key=lambda status: status.favorite_count, reverse=False)
    else:
        return sorted(statuses, key=lambda status: status.favorite_count, reverse=True)


def select_statuses(statuses, count):
    """
    つぶやきの最初のものからcountの数の{id, つぶやき}辞書を取得。(countが0以下の場合は空の辞書を返す)
    """
    result_dictionary = {}
    if count < 1:
        return result_dictionary
    loop_count = 0
    for status in statuses:
        loop_count += 1
        result_dictionary.setdefault(loop_count, status)
        if loop_count >= count:
            break
    return result_dictionary


def collect_user_tweet(user_screen_name):
    """
    Twitterのuser_screen_name(@taroのtaroの部分)のユーザーのつぶやきをDBに登録します。
    """
    for status in search_user_tweet(user_screen_name):
        user_id = status.user.id
        tweet_id = status.id
        tweet_text = status.text
        tweet_datetime = status.created_at
        try:
            twitter_tweet_repository.add_tweet(user_id, tweet_id, tweet_text, tweet_datetime)
        except:
            print('何らかのエラー発生')


def search_user_tweet(user_screen_name):
    """
    Twitterのuser_screen_name(@taroのtaroの部分)のユーザーのつぶやきを200件取得します。
    """
    api = prepare_twitter_api()
    return api.user_timeline(screen_name=user_screen_name, count=200)
