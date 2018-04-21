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
    api = twitter_common_service.prepare_twitter_api(user_screen_name)
    follow_count = 0
    i = 0
    max_id = None
    search_count = 100
    stop_second = 90
    max_count = int(max_count)
    friend_ids = api.friends_ids(user_screen_name)

    # 対象ユーザーがDBにまだ登録されていないなら登録する。
    if twitter_user_repository.search_user(user_screen_name) is None:
        print("user:{}はDBに登録されてなかったからDB登録するよ".format(user_screen_name))
        search_insert_user(user_screen_name, user_screen_name)
        print("user:{}はDBに登録されてなかったからDB登録したよ".format(user_screen_name))

    for i in range(10):
        print('{}回目の検索'.format(str(i + 1)))
        if max_id is None:
            search_results = api.search(q=query, count=search_count)
        else:
            search_results = api.search(q=query, count=search_count, max_id=max_id)
        for status in search_results:
            print('---------------------------------------')
            if status.user.id in friend_ids:
                print('user_id:{}はすでにフォローしてたからフォローしなかったよ'.format(status.user.id))
                continue
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
    # プロフィールか自己紹介に公序良俗に反する言葉が含まれていた場合はフォローしない
    if common_service.contain_dangerous_word(status.user.name) or common_service.contain_dangerous_word(
            status.user.description):
        print("{}は公序良俗に反する言葉が含まれていたからフォローしなかったよ".format(status.user.screen_name))
        return False
    # フォロー履歴が1年以内にあればフォローしない
    own_user_id = own_user.user_id
    target_user_id = status.user.id
    follow_opt = twitter_follow_repository.search_follow(own_user_id, target_user_id)
    year_ago = timeutil_service.culc_before_year(1)
    if (follow_opt is not None) and (follow_opt.upd_datetime > year_ago):
        print("{}は1年以内にフォローしたことあるからフォローしなかったよ".format(target_user_screen_name))
        return False
    # フォロー
    api = twitter_common_service.prepare_twitter_api(user_screen_name)
    follow_user(api, own_user_id, target_user_id)
    return True


def follow_user(api, own_user_id, user_id):
    """
    指定したapi/own_user_idのユーザーで、user_idのユーザーのフォロー処理を行う
    return: True or False（True = フォロー成功）
    """
    try:
        api.create_friendship(user_id)
        print('user_id:{}でuser_id:{}をフォローしたよ'.format(own_user_id, user_id))
        follow_opt = twitter_follow_repository.search_follow(own_user_id, user_id)
        # 初めてのフォローの場合
        if follow_opt is None:
            twitter_follow_repository.add_follow(own_user_id, user_id)
            print('user_id:{}でuser_id:{}を初めてフォローしたことをDB保存したよ'.format(own_user_id, user_id))
        # 2度目以降のフォローの場合はdelete_flgをfalseに変更する
        else:
            twitter_follow_repository.update_follow_delete_flg(own_user_id, user_id, False)
            print('user_id:{}でuser_id:{}を2回目以降のフォローしたことをDB保存したよ'.format(own_user_id, user_id))
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
    print('---------------- user:{}でアンフォロー処理開始'.format(user_screen_name))
    api = twitter_common_service.prepare_twitter_api(user_screen_name)
    unfollow_count = 0
    stop_second = 90
    max_count = int(max_count)

    user_opt = twitter_user_repository.search_user(user_screen_name)
    # 対象ユーザーがDBにまだ登録されていないなら登録する。
    if user_opt is None:
        print("user:{}はDBに登録されてなかったからDB登録するよ".format(user_screen_name))
        search_insert_user(user_screen_name, user_screen_name)
        user_opt = twitter_user_repository.search_user(user_screen_name)

    own_user_id = user_opt.user_id
    friend_ids = api.friends_ids(user_screen_name)
    for friend_id in friend_ids:
        unfollow_success = unfollow_target_user(api, own_user_id, friend_id)
        if unfollow_success:
            unfollow_count = unfollow_count + 1
            print('「{}」人アンフォローした'.format(str(unfollow_count)))
            if unfollow_count % 3 == 0:
                print('「{}」人一気にアンフォローした...'.format(str(unfollow_count)))
                timeutil_service.sleep(stop_second)
        # アンフォロー人数が上限に達したら処理終了
        if unfollow_count >= max_count:
            print('---------------- user:{}でアンフォロー処理終了(フォロー人数:{})'.format(user_screen_name, str(unfollow_count)))
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
        twitter_follow_repository.update_follow_delete_flg(own_user_id, friend_id, True)
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
        twitter_follow_repository.update_follow_delete_flg(own_user_id, friend_id, True)
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
def collect_user_tweets(user_screen_name, target_screen_name):
    """
    user_screen_name(@taroのtaroの部分)のTwitterユーザーのつぶやきを、現状の最新ツイートから古いツイートを順次DBに最大2000件登録
    """
    pre_oldest_tweet_id = None
    # 連続でAPIアクセスするとAPIアクセス上限になるかもしれないから10回だけのループにしておく。
    for i in range(10):
        print('{}回目のループ開始'.format(str(i + 1)))
        oldest_tweet_id = twitter_tweet_repository.search_oldest_tweet(target_screen_name)
        # 2回以上ツイートが更新されなければ、最新のツイートがないということで処理終了
        if (pre_oldest_tweet_id is not None) and pre_oldest_tweet_id == oldest_tweet_id:
            print('最新ツイートもうないっぽかったから{}回目の検索前に処理終了'.format(str(i + 1)))
            break

        user_id = twitter_tweet_repository.search_user_id(target_screen_name)
        # 最新のつぶやきから200件ずつ検索してDB保存していく
        tweet_count = 0
        if oldest_tweet_id is None:
            tweets = twitter_common_service.search_user_tweets(user_screen_name, target_screen_name)
            for tweet in tweets:
                tweet_count = tweet_count + 1
                try:
                    twitter_tweet_repository.add_tweet(user_id, tweet.id, tweet.text, tweet.created_at)
                    print('{} tweet_id:{}のツイート登録完了'.format(tweet_count, tweet.id))
                except Exception as e:
                    print("例外args:{}".format(e.args))
            # twitter_tweet_repository.add_tweets(user_id, tweets)
        else:
            tweets = twitter_common_service.search_user_tweets_before(user_screen_name, target_screen_name, oldest_tweet_id)
            # twitter_tweet_repository.add_tweets(user_id, tweets)
            for tweet in tweets:
                tweet_count = tweet_count + 1
                try:
                    twitter_tweet_repository.add_tweet(user_id, tweet.id, tweet.text, tweet.created_at)
                    print('{} tweet_id:{}のツイート登録完了'.format(tweet_count, tweet.id))
                except Exception as e:
                    print("例外args:{}".format(e.args))

        pre_oldest_tweet_id = oldest_tweet_id


def collect_user_tweets_diff(user_screen_name, target_screen_name):
    """
    user_screen_name(@taroのtaroの部分)のTwitterユーザーのつぶやきを、現状の最新ツイートから新しいツイートを順次DBに最大2000件登録
    APIアクセス数減らすため、DB保存対象となる最新ツイートがなくなれば処理終了する
    """
    pre_latest_tweet_id = None
    insert_count = 0
    # 連続でAPIアクセスするとAPIアクセス上限になるかもしれないから10回だけのループにしておく。
    for i in range(10):

        print('{}回目のループ開始'.format(str(i + 1)))
        latest_tweet_id = twitter_tweet_repository.search_latest_tweet(target_screen_name)

        # 2回以上ツイートが更新されなければ、最新のツイートがないということで処理終了
        if (pre_latest_tweet_id is not None) and pre_latest_tweet_id == latest_tweet_id:
            print('最新ツイートもうないっぽかったから{}回目の検索前に処理終了'.format(str(i + 1)))
            break

        user_id = twitter_tweet_repository.search_user_id(target_screen_name)
        # 最新のつぶやきから200件ずつ検索してDB保存していく
        if latest_tweet_id is None:
            tweets = twitter_common_service.search_user_tweets(user_screen_name, target_screen_name)
            for tweet in tweets:
                try:
                    twitter_tweet_repository.add_tweet(user_id, tweet.id, tweet.text, tweet.created_at)
                    insert_count = insert_count + 1
                    print('{}件目 tweet_id:{}のツイート登録完了'.format(insert_count, tweet.id))
                except Exception as e:
                    print("例外args:{}".format(e.args))
        else:
            tweets = twitter_common_service.search_user_tweets_after(user_screen_name, target_screen_name, latest_tweet_id)
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
def search_insert_user(user_screen_name, target_screen_name):
    """
    user_screen_nameでTwitterユーザーを検索して、DBに保存します。
    """
    user = twitter_common_service.search_user(user_screen_name, target_screen_name)
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


##############################
# 話題のつぶやきを検索してリツイート
##############################
def search_popular_tweet_and_retweet(user_screen_name, query, retweet_count):
    """
    user_screen_nameのTwitterユーザーでqueryで話題のつぶやきを探してretweet_count個引用リツイートする
    """
    # twitterのアクセス情報
    api = twitter_common_service.prepare_twitter_api(user_screen_name)
    search_results = twitter_common_service.search_tweet(api, query, 'popular', 100)

    if len(search_results) == 0:
        print('ツイート見つからなかったす。')
        return

    # いいね数の多い順のつぶやき一覧取得
    statuses = twitter_common_service.sort_by_favorite_count(search_results, True)
    # いいね数の多いretweet_count個のつぶやき取得
    top_statuses_dictionary = twitter_common_service.select_statuses(statuses, retweet_count)
    for status in top_statuses_dictionary.values():
        # リツイート文章作る
        tweet_link = 'https://twitter.com/{}/status/{}'.format(status.user.screen_name, status.id)
        comment = common_service.create_random_comment()
        retweet_text = comment + '\n' + tweet_link
        # リツイートする
        api.update_status(status=retweet_text)


def search_popular_tweet_and_retweet_only(user_screen_name, query, retweet_count):
    """
    user_screen_nameのTwitterユーザーでqueryで話題のつぶやきを探してretweet_count個リツイートする
    """
    # twitterのアクセス情報
    api = twitter_common_service.prepare_twitter_api(user_screen_name)
    search_results = twitter_common_service.search_tweet(api, query, 'popular', 100)

    if len(search_results) == 0:
        print('ツイート見つからなかったす。')
        return

    # いいね数の多い順のつぶやき一覧取得
    statuses = twitter_common_service.sort_by_favorite_count(search_results, True)
    # いいね数の多いretweet_count個のつぶやき取得
    top_statuses_dictionary = twitter_common_service.select_statuses(statuses, retweet_count)
    for status in top_statuses_dictionary.values():
        # リツイートリンク作る
        tweet_link = 'https://twitter.com/{}/status/{}'.format(status.user.screen_name, status.id)
        # リツイートする
        api.update_status(status=tweet_link)


def search_unpopular_tweet_and_tweet(user_screen_name, query):
    """
    user_screen_nameのTwitterユーザーでqueryで話題でないつぶやきを探して真似してツイートする
    """
    # twitterのアクセス情報
    api = twitter_common_service.prepare_twitter_api(user_screen_name)
    search_results = twitter_common_service.search_tweet(api, query, 'popular', 100)

    if len(search_results) == 0:
        print('ツイート見つからなかったす。')
        return

    # いいね数の少ない順のつぶやき一覧取得
    statuses = twitter_common_service.sort_by_favorite_count(search_results, False)
    # いいね数の多い1つのつぶやき取得
    unpopular_status_dictionary = twitter_common_service.select_statuses(statuses, 1)
    for status in unpopular_status_dictionary.values():
        # ツイートする
        api.update_status(status=status.text)
