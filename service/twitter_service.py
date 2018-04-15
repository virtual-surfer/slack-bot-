# coding=utf-8
import tweepy
import os
from datetime import datetime
from repository import twitter_tweet_repository
from repository import twitter_user_repository


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


def collect_user_tweets(user_screen_name):
    """
    user_screen_name(@taroのtaroの部分)のTwitterユーザーのつぶやきを、現状の最新ツイートから古いツイートを順次DBに最大2000件登録
    """
    # 連続でAPIアクセスするとAPIアクセス上限になるかもしれないから10回だけのループにしておく。
    for i in range(10):
        print('{}回目のループ開始'.format(str(i + 1)))
        oldest_tweet_id = twitter_tweet_repository.search_oldest_tweet(user_screen_name)
        user_id = twitter_tweet_repository.search_user_id(user_screen_name)
        # 最新のつぶやきから200件ずつ検索してDB保存していく
        tweet_count = 0
        if oldest_tweet_id is None:
            tweets = search_user_tweets(user_screen_name)
            for tweet in tweets:
                tweet_count = tweet_count + 1
                try:
                    twitter_tweet_repository.add_tweet(user_id, tweet.id, tweet.text, tweet.created_at)
                    print('{} tweet_id:{}のツイート登録完了'.format(tweet_count, tweet.id))
                except Exception as e:
                    print("例外args:{}".format(e.args))
            # twitter_tweet_repository.add_tweets(user_id, tweets)
        else:
            tweets = search_user_tweets_before(user_screen_name, oldest_tweet_id)
            # twitter_tweet_repository.add_tweets(user_id, tweets)
            for tweet in tweets:
                tweet_count = tweet_count + 1
                try:
                    twitter_tweet_repository.add_tweet(user_id, tweet.id, tweet.text, tweet.created_at)
                    print('{} tweet_id:{}のツイート登録完了'.format(tweet_count, tweet.id))
                except Exception as e:
                    print("例外args:{}".format(e.args))


def insert_tweet(status):
    """
    statusからDB保存する情報を取り出してDB保存する
    """
    user_id = status.user.id
    tweet_id = status.id
    tweet_text = status.text
    tweet_datetime = status.created_at
    now = datetime.now()
    try:
        twitter_tweet_repository.add_tweet(user_id, tweet_id, tweet_text, tweet_datetime)
        print('{} tweet_id:{}のつぶやきをDB保存しました。'.format(now, tweet_id))
    except Exception as e:
        print("{} 例外args:{}".format(now, e.args))


def insert_tweets(statuses):
    """
    statusからDB保存する情報を取り出してDB保存する
    """
    for status in statuses:
        user_id = status.user.id
        tweet_id = status.id
        tweet_text = status.text
        tweet_datetime = status.created_at
        now = datetime.now()
        try:
            twitter_tweet_repository.add_tweet(user_id, tweet_id, tweet_text, tweet_datetime)
            print('{} tweet_id:{}のつぶやきをDB保存しました。'.format(now, tweet_id))
        except Exception as e:
            print("{} 例外args:{}".format(now, e.args))


def search_insert_user(user_screen_name):
    """
    user_screen_nameでTwitterユーザーを検索して、DBに保存します。
    """
    user = search_user(user_screen_name)
    try:
        twitter_user_repository.add_user(user.id, user.screen_name, user.created_at)
        print('user.screen_name:{}をDB保存しました。'.format(user.screen_name))
    except Exception as e:
        print("例外args:{}", e.args)


def dialogue_with_twitter_user(message, user_screen_name, text):
    """
    textに対しての返答として最適なものを、user_screen_nameのTwitterユーザーの持つテキストから選択してテキスト形式で返します。
    """


def search_user(user_screen_name):
    """
    Twitterのuser_screen_name(@taroのtaroの部分)のユーザーを取得します。
    """
    api = prepare_twitter_api()
    return api.get_user(screen_name=user_screen_name)


def search_user_tweets(user_screen_name):
    """
    Twitterのuser_screen_name(@taroのtaroの部分)のユーザーのつぶやきを200件取得します。
    """
    api = prepare_twitter_api()
    return api.user_timeline(screen_name=user_screen_name, count=200)


def search_user_tweets_after(user_screen_name, since_id):
    """
    Twitterのuser_screen_name(@taroのtaroの部分)のユーザーのつぶやきをsince_id以降で上限200件取得します。
    """
    api = prepare_twitter_api()
    return api.user_timeline(screen_name=user_screen_name, since_id=since_id, count=200)


def search_user_tweets_before(user_screen_name, max_id):
    """
    Twitterのuser_screen_name(@taroのtaroの部分)のユーザーのつぶやきをmax_id以前で上限200件取得します。
    """
    api = prepare_twitter_api()
    return api.user_timeline(screen_name=user_screen_name, max_id=max_id, count=200)


def search_user_tweets_fromto(user_screen_name, since_id, max_id):
    """
    Twitterのuser_screen_name(@taroのtaroの部分)のユーザーのつぶやきをsince_id以降、max_id以前のもので上限200件取得します。
    """
    api = prepare_twitter_api()
    return api.user_timeline(screen_name=user_screen_name, since_id=since_id, max_id=max_id, count=200)
