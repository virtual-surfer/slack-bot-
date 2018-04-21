# coding=utf-8
import random
from service.twitter import twitter_service
from service import timeutil_service


# ######################### 処理実行時間一覧 #########################

# 前提 : batchは10分毎に起動される。2時~6時はツイート閲覧数少ないと見込んで処理しない。
# 本に関するつぶやき : 2時間ごと
# アンフォロー : 2日に1回 18時
# フォロー : 2日に1回 20時
# メンション=いいね/リツイート=いいね or リツイートする : (TODO:1日の上限は設ける)

# ##################################################################

# ################## 各種変数(基本的にはここだけ触る) ##################

user_screen_name = 'virtual_techX'
max_follow_count_every_other_day = 15
max_unfollow_count_every_other_day = 15
follow_target_word_list = ['プログラミング', 'プログラミング初心者', 'Webエンジニア', 'ITベンチャー', 'startup', '起業', '投資',
                           'デザイン', 'はてなブログ', 'Python', 'Ruby', 'Go', 'Java', 'Javascript', 'Node.js', 'React',
                           'Angular', 'AR', 'VR', '機械学習', 'deep learning', 'MR', 'china tech', 'スタートアップ', '仮想通貨',
                           'MONA', 'monapy', 'もにゃ', 'xrp', 'XEM', 'NEM', 'ブロックチェーン', 'ETH', 'Ethereum', 'QSP',
                           'TRX', 'トロン', 'crypt currency', '仮想現実', 'Ripple', 'BTC', 'BCH', 'ビットコイン']

# ##################################################################


def execute():
    current_hour = timeutil_service.current_datetime().hour
    # 2時~8時はおやすみ（処理しない）
    if 2 < current_hour < 8:
        return

    # 10分に1回 TODO:処理増えてきたら->自分にメンションが来ているかを確認してツイートタスクに詰める
    # 「メンションきているものにレスポンス文章作ってツイートする」タスクを1分間に1つぶやきの頻度で返す
    print('{} TODO current_hour:{}'.format(user_screen_name, current_hour))

    current_minute = timeutil_service.current_datetime().minute
    # 定期実行タスクに関しては0分~10分以外はおやすみ（処理しない）
    if 10 < current_minute <= 59:
        return

    # 偶数時間(フォロー処理時間以外)につぶやき
    # done 適当にツイート検索してツイート
    # TODO: DB保存している女子高生のつぶやきでつぶやき時間の近いもの真似して投稿
    if current_hour % 2 == 0 and current_hour != 18 and current_hour != 20:
        print('{} TODO2 current_hour:{}'.format(user_screen_name, current_hour))
        # ↓精度低いから成長させよう
        # twitter_service.search_unpopular_tweet_and_tweet(user_screen_name, random.choice(follow_target_word_list))
    # 奇数時間につぶやき
    # done 適当にツイート検索して引用リツイート
    # TODO: 話題のつぶやきの引用リツイート
    if current_hour % 2 != 0 and current_hour != 19:
        twitter_service.search_popular_tweet_and_retweet(user_screen_name, random.choice(follow_target_word_list))
    # 指定時間にセール情報と新着情報
    if current_hour == 11 or current_hour == 15 or current_hour == 19:
        print('{} TODO3 current_hour:{}'.format(user_screen_name, current_hour))

    today = timeutil_service.current_datetime().day
    # 偶数日(2日に1回)はおやすみ（処理しない）
    if today % 2 == 0:
        return
    # done 自動アンフォロー機能
    if current_hour == 18:
        twitter_service.unfollow(user_screen_name, max_unfollow_count_every_other_day)
    # done  自動フォロー機能
    if current_hour == 20:
        twitter_service.search_follow(user_screen_name, random.choice(follow_target_word_list), max_follow_count_every_other_day)
