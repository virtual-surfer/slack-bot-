# coding=utf-8
import tweepy
import os
from service import timeutil_service
from service import common_service
from service.twitter import twitter_common_service
from repository import twitter_tweet_repository
from repository import twitter_user_repository
from repository import twitter_follow_repository


################
# 自動フォロー処理
################
def search_follow(user_screen_name, query, max_count):
    """
    指定したuser_screen_nameのユーザーで、queryで検索したツイッターユーザーをmax_count数フォローして、DBにフォローデータを登録
    """
    api = twitter_common_service.prepare_twitter_api()
    follow_count = 0
    i = 0
    max_id = None
    search_count = 100
    stop_second = 90
    max_count = int(max_count)

    for i in range(10):
        print('{}回目の検索'.format(str(i + 1)))
        if max_id is None:
            search_results = api.search(q=query, count=search_count)
        else:
            search_results = api.search(q=query, count=search_count, max_id=max_id)
        for status in search_results:
            print('---------------------------------------')
            follow_success = follow_target_user(user_screen_name, status)
            if follow_success is True:
                follow_count = follow_count + 1
                # 一気にフォローすると危険アカウント認定される恐れあるため、処理一時中断
                if follow_count % 10 == 0:
                    print('{}人一気にフォローした...'.format(follow_count))
                    timeutil_service.sleep_second(stop_second)
            print('「{}」人フォローした'.format(str(follow_count)))
            if follow_count >= max_count:
                print('{}人フォロー完了したから処理終了'.format(str(follow_count)))
                return
        # 一番古いツイートよりも古いツイートを探すため、一番古いツイートID取得
        max_id = search_results[-1].id
        # 一気にフォローすると危険アカウント認定される恐れあるため、処理一時中断
        print('{}人チェックした...'.format(search_count))
        timeutil_service.sleep_second(stop_second)
    print('{}回検索したから処理終了'.format(str(i + 1)))


def follow_target_user(user_screen_name, status):
    """
    指定したuser_screen_nameのユーザーで、statusのユーザーの自動フォロー処理を行う
    return: True or False（True = フォロー成功）
    """
    target_user_screen_name = status.user.screen_name
    # フォロワーが300人以下ならフォローしない
    followers_count = status.user.followers_count
    follow_target_min_follower_count = 300
    if followers_count < follow_target_min_follower_count:
        print("{}はフォロワーが{}人以下だったからフォローしなかったよ".format(target_user_screen_name, follow_target_min_follower_count))
        return False
    # user_screen_nameがDBに保存されていない場合はフォローしない
    own_user = twitter_user_repository.search_user(user_screen_name)
    if own_user is None:
        print("{}はDBに登録されてなかったよ".format(user_screen_name))
        return False
    # プロフィールか自己紹介に公序良俗に反する言葉が含まれていた場合はフォローしない
    if common_service.contain_dangerous_word(status.user.name) or common_service.contain_dangerous_word(
            status.user.description):
        print("{}は公序良俗に反する言葉が含まれていたからフォローしなかったよ".format(status.user.screen_name))
        return False
    # フォロー履歴が半年以内にあればフォローしない
    own_user_id = own_user.user_id
    target_user_id = status.user.id
    follow_opt = twitter_follow_repository.search_follow(own_user_id, target_user_id)
    year_ago = timeutil_service.culc_before_year(1)
    if (follow_opt is not None) and (follow_opt.upd_datetime > year_ago):
        print("{}は既にフォローしてたか、1年以内にフォローしたことあるからフォローしなかったよ".format(target_user_screen_name))
        return False
    # フォロー
    api = twitter_common_service.prepare_twitter_api()
    follow_user(api, own_user_id, target_user_id)
    return True


def follow_user(api, own_user_id, user_id):
    """
    指定したapi/own_user_idのユーザーで、user_idのユーザーのフォロー処理を行う
    return: True or False（True = フォロー成功）
    """
    try:
        api.create_friendship(user_id)
        print('user_id{}でuser_id{}をフォローしたよ'.format(own_user_id, user_id))
        twitter_follow_repository.add_follow(own_user_id, user_id)
        return True
    except Exception as e:
        print("例外args:{}".format(e.args))
        return False


###################
# 自動アンフォロー処理
###################
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
            if unfollow_count % 5 == 0:
                print('「{}」人一気にアンフォローしたから60秒待機...'.format(str(unfollow_count)))
                timeutil_service.sleep(60)
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
        print("ユーザー(user_id:{})は手動フォローしたユーザーだから無視したよ".format(friend_id))
        return False
    # 3日以内にフォローしたユーザーは対象から除外
    if follow_opt.upd_datetime >= timeutil_service.minus_day(3):
        print("ユーザー(user_id:{})は3日以内にフォローしたユーザーだから無視したよ".format(friend_id))
        return False
    # フォローされている場合は対象から除外
    follower_ids = api.followers_ids(own_user_id)
    if friend_id in follower_ids:
        print("ユーザー(user_id:{})にはフォローされていたから無視したよ".format(friend_id))
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


#####################
# ツイートまとめ生成処理
#####################
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


##################
# ツイートDB保存処理
##################
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


def collect_user_tweets_diff(user_screen_name):
    """
    user_screen_name(@taroのtaroの部分)のTwitterユーザーのつぶやきを、現状の最新ツイートから新しいツイートを順次DBに最大2000件登録
    APIアクセス数減らすため、DB保存対象となる最新ツイートがなくなれば処理終了する
    """
    pre_latest_tweet_id = None
    insert_count = 0
    # 連続でAPIアクセスするとAPIアクセス上限になるかもしれないから10回だけのループにしておく。
    for i in range(10):

        print('{}回目のループ開始'.format(str(i + 1)))
        latest_tweet_id = twitter_tweet_repository.search_latest_tweet(user_screen_name)

        # 2回以上ツイートが更新されなければ、最新のツイートがないということで処理終了
        if (pre_latest_tweet_id is not None) and pre_latest_tweet_id == latest_tweet_id:
            print('最新ツイートもうないっぽかったから{}回目の検索前に処理終了'.format(str(i + 1)))
            break

        user_id = twitter_tweet_repository.search_user_id(user_screen_name)
        # 最新のつぶやきから200件ずつ検索してDB保存していく
        if latest_tweet_id is None:
            tweets = twitter_common_service.search_user_tweets(user_screen_name)
            for tweet in tweets:
                try:
                    twitter_tweet_repository.add_tweet(user_id, tweet.id, tweet.text, tweet.created_at)
                    insert_count = insert_count + 1
                    print('{}件目 tweet_id:{}のツイート登録完了'.format(insert_count, tweet.id))
                except Exception as e:
                    print("例外args:{}".format(e.args))
            # twitter_tweet_repository.add_tweets(user_id, tweets)
        else:
            tweets = twitter_common_service.search_user_tweets_after(user_screen_name, latest_tweet_id)
            # twitter_tweet_repository.add_tweets(user_id, tweets)
            for tweet in tweets:
                try:
                    twitter_tweet_repository.add_tweet(user_id, tweet.id, tweet.text, tweet.created_at)
                    insert_count = insert_count + 1
                    print('{}件目 tweet_id:{}のツイート登録完了'.format(insert_count, tweet.id))
                except Exception as e:
                    print("例外args:{}".format(e.args))

        pre_latest_tweet_id = latest_tweet_id

    print('\n{}件のツイート保存完了'.format(insert_count))


##################
# ユーザーDB保存処理
##################
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


##########################
# ツイッターユーザーと雑談機能
##########################
def dialogue_with_twitter_user(message, user_screen_name, text):
    """
    textに対しての返答として最適なものを、user_screen_nameのTwitterユーザーの持つテキストから選択してテキスト形式で返します。
    """
