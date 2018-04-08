# coding=utf-8
import tweepy


def prepare_twitter_api():
    """
    TwitterのAPIアクセスキーを取得
    """
    auth = tweepy.OAuthHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])
    auth.set_access_token(os.environ['ACCESS_TOKEN'], os.environ['ACCESS_TOKEN_SECRET'])
    return tweepy.API(auth)


def search_tweet(api, word,result_type, count):
    """
    Twitterでwordで一致する日本語つぶやき情報を取得
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
        result_text = '\n{}@({})\n{}\n({}いいね){}\n'.format(user.name, user.screen_name, status.text, str(fav_count), tweet_link)
        post_text = '{}-------------------------------------------------------{}'.format(post_text, result_text)
    return post_text


def sort_by_favorite_count(statuses, is_asc):
    """
    引数で与えられたつぶやきを「いいね」の少ない順で並び替えて返す。(is_ascがfalseなら多い順)
    statusesが空の場合は空の辞書を返す
    """
    # 辞書{つぶやき, いいね数}に詰めていく
    result_dictionary = {}
    for status in statuses:
        favorite_count = status.favorite_count
        result_dictionary.setdefault(status, favorite_count)
    if is_asc:
        return sorted(result_dictionary.items(), key=lambda x: x[1])
    else:
        return sorted(result_dictionary.items(), key=lambda x: -x[1])
