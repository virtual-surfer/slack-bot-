# coding=utf-8
import tweepy
import os
from service import timeutil_service
from service import common_service
from service.twitter import twitter_common_service
from repository import twitter_tweet_repository
from repository import twitter_user_repository
from repository import twitter_follow_repository


# 自動フォロー処理
def search_follow(user_screen_name, query, max_count):
    """
    指定したuser_screen_nameのユーザーで、queryで検索したツイッターユーザーをmax_count数フォローして、DBにフォローデータを登録
    """
    api = twitter_common_service.prepare_twitter_api()
    follow_count = 0
    i = 0
    max_id = None
    max_count = int(max_count)

    for i in range(10):
        print('{}回目の検索'.format(str(i + 1)))
        if max_id is None:
            search_results = api.search(q=query, count=100)
        else:
            search_results = api.search(q=query, count=100, max_id=max_id)
        for status in search_results:
            print('---------------------------------------')
            follow_success = follow_target_user(api, user_screen_name, status)
            if follow_success is True:
                follow_count = follow_count + 1
            print('「{}」人フォローした'.format(str(follow_count)))
            if follow_count >= max_count:
                print('{}人フォロー完了したから処理終了'.format(str(follow_count)))
                return
        # 一番古いツイートよりも古いツイートを探すため、一番古いツイートID取得
        max_id = search_results[-1].id
        # 一気にフォローすると危険アカウント認定される恐れあるため、1分間停止
        timeutil_service.sleep_second(60)
    print('{}回検索したから処理終了'.format(str(i + 1)))


def follow_target_user(user_screen_name, status):
    """
    指定したuser_screen_nameのユーザーで、statusのユーザーの自動フォロー処理を行う
    return: True or False（True = フォロー成功）
    """
    target_user_screen_name = status.user.screen_name
    # フォロワーが300人以下ならフォローしない
    followers_count = status.user.followers_count
    if followers_count < 300:
        print("{}はフォロワーが200人以下だったからフォローしなかったよ".format(target_user_screen_name))
        return False
    # user_screen_nameがDBに保存されていない場合はフォローしない
    own_user = twitter_user_repository.search_user(user_screen_name)
    if own_user is None:
        print("{}はDBに登録されてなかったよ".format(user_screen_name))
        return False
    # プロフィールか自己紹介に公序良俗に反する言葉が含まれていた場合はフォローしない
    if common_service.contain_dangerous_word(status.user.name) or common_service.contain_dangerous_word(
            status.user.description):
        return False
    # フォロー履歴が半年以内にあればフォローしない
    own_user_id = own_user.user_id
    target_user_id = status.user.id
    follow_opt = twitter_follow_repository.search_follow(own_user_id, target_user_id)
    year_ago = timeutil_service.culc_before_year(1)
    if (follow_opt is not None) and (follow_opt.upd_datetime < year_ago):
        print("{}は既にフォローしてたか、1年以内にフォローしたことあるからフォローしなかったよ".format(target_user_screen_name))
        return False
    # フォロー
    api = twitter_common_service.prepare_twitter_api()
    follow_user(api, own_user_id, user_id)


def follow_user(api, own_user_id, user_id):
    """
    指定したapi/own_user_idのユーザーで、user_idのユーザーのフォロー処理を行う
    return: True or False（True = フォロー成功）
    """
    try:
        api.create_friendship(user_id)
        print('{}で{}をフォローしたよ'.format(own_user.user_screen_name, target_user_screen_name))
        twitter_follow_repository.add_follow(own_user_id, user_id)
        return True
    except Exception as e:
        print("例外args:{}".format(e.args))
        return False


# 自動アンフォロー処理
def unfollow(user_screen_name, max_count):
    """
    指定したuser_screen_nameのユーザーで、上限max_countだけフォローを外していく。
    """
    api = twitter_common_service.prepare_twitter_api()
    unfollow_count = 0
    max_count = int(max_count)

    user_opt = twitter_user_repository.search_user(user_screen_name)
    if user_opt is None:
        print("{}はDBに登録されてなかったよ".format(user_screen_name))
        return
    own_user_id = user_opt.user_id

    friend_ids = api.friends_ids(user_screen_name)
    for friend_id in friend_ids:
        unfollow_success = unfollow_target_user(api, own_user_id, friend_id)
        if unfollow_success:
            unfollow_count = unfollow_count + 1
            print('「{}」人アンフォローした'.format(str(unfollow_count)))
        # アンフォロー人数が上限に達したら処理終了
        if unfollow_count >= max_count:
            print('{}人アンフォロー完了したから処理終了'.format(str(unfollow_count)))
            return


def unfollow_target_user(api, own_user_id, friend_id):
    """
    指定したown_user_idのユーザーで、friend_idのユーザーの自動アンフォロー処理を行う
    return: True or False（True = アンフォロー成功）
    """
    follow_opt = twitter_follow_repository.search_follow(own_user_id, friend_id)
    # フォローテーブルが登録されていない(フォローが手動で行われた)場合は意志を持ってフォローしているためアンフォロー対象から除外
    if (follow_opt is None) or (follow_opt.auto_flg is False):
        print("ユーザー(friend_id:{})は手動フォローしたユーザーだから無視したよ".format(friend_id))
        return False
    # 3日以内にフォローしたユーザーは対象から除外
    if follow_opt.upd_datetime >= timeutil_service.minus_day(3):
        print("ユーザー(friend_id:{})は3日以内にフォローしたユーザーだから無視したよ".format(friend_id))
        return False
    # フォローされている場合は対象から除外
    follower_ids = api.followers_ids(user_screen_name)
    if friend_id in follower_ids:
        print("ユーザー(friend_id:{})にはフォローされていたから無視したよ".format(friend_id))
        return False
    # フォロー外して、DBで対象ユーザーのフォロー情報更新(del_flgをTrueに)
    try:
        api.destroy_friendship(friend_id)
        print("user_id:{}のフォロー外したよ".format(friend_id))
        twitter_follow_repository.update_follow_delete_flg(own_user_id, friend_id)
        return True
    except Exception as e:
        print("例外args:{}".format(e.args))
        return False


def unfollow_user(api, own_user_id, friend_id):
    """
    指定したown_user_idのユーザーで、friend_idのユーザーのアンフォロー処理を行う
    return: True or False（True = アンフォロー成功）
    """
    try:
        api.destroy_friendship(friend_id)
        print("user_id:{}のフォロー外したよ".format(friend_id))
        twitter_follow_repository.update_follow_delete_flg(own_user_id, friend_id)
        return True
    except Exception as e:
        print("例外args:{}".format(e.args))
        return False


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
            tweets = twitter_common_service.search_user_tweets(user_screen_name)
            for tweet in tweets:
                tweet_count = tweet_count + 1
                try:
                    twitter_tweet_repository.add_tweet(user_id, tweet.id, tweet.text, tweet.created_at)
                    print('{} tweet_id:{}のツイート登録完了'.format(tweet_count, tweet.id))
                except Exception as e:
                    print("例外args:{}".format(e.args))
            # twitter_tweet_repository.add_tweets(user_id, tweets)
        else:
            tweets = twitter_common_service.search_user_tweets_before(user_screen_name, oldest_tweet_id)
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
    user = twitter_common_service.search_user(user_screen_name)
    print('{}をTwitterから取得できたよ'.format(user_screen_name))
    try:
        twitter_user_repository.add_user(user.id, user.screen_name, user.created_at)
        print('user.screen_name:{}をDB保存しました。'.format(user.screen_name))
    except Exception as e:
        print("例外args:{}", e.args)


def dialogue_with_twitter_user(message, user_screen_name, text):
    """
    textに対しての返答として最適なものを、user_screen_nameのTwitterユーザーの持つテキストから選択してテキスト形式で返します。
    """
