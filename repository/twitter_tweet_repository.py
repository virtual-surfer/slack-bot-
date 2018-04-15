# coding=utf-8
from repository import common_repository
from entity.twitter_tweet_entity import TwitterTweet
from entity.twitter_user_entity import TwitterUser
from repository import twitter_user_repository
from sqlalchemy.sql import select
from sqlalchemy.sql import func
from sqlalchemy.sql import desc


# 登録処理
def add_tweet(twitter_user_id, tweet_id, text, datetime):
    # トランザクション開始
    session = common_repository.create_session()
    # user追加
    test_user = TwitterTweet(twitter_user_id=twitter_user_id, twitter_tweet_id=tweet_id, tweet_text=text, tweet_datetime=datetime)
    session.add(test_user)
    # 変更をコミット
    session.commit()
    session.close()


def add_tweets(user_id, tweets):
    # トランザクション開始
    session = common_repository.create_session()
    # bulkで一括user追加
    print('ツイートの一括登録処理開始！！！')
    session.bulk_save_objects(
        [TwitterTweet(twitter_user_id=user_id, twitter_tweet_id=tweet.id, tweet_text=tweet.text, tweet_datetime=tweet.created_at)
         for tweet in tweets], return_defaults=True)
    # 変更をコミット
    print('ツイートの一括登録処理完了！！！')
    session.commit()


def search_latest_tweet(user_screen_name):
    # トランザクション開始
    session = common_repository.create_session()
    # user_screen_nameからuser_idを取得する
    user = twitter_user_repository.search_user(user_screen_name)
    user_id = user.twitter_user_id
    # 最新のツイートを取得する
    tweet = TwitterTweet
    latest_tweet = session.query(tweet).filter(tweet.twitter_user_id == user_id).order_by(desc(tweet.twitter_tweet_id)).first()
    if latest_tweet is None:
        session.close()
        return None
    else:
        latest_tweet_id = latest_tweet.twitter_tweet_id
        session.close()
        print('------------------- latest_tweet_id:{}'.format(latest_tweet_id))
        return latest_tweet_id


def search_oldest_tweet(user_screen_name):
    # トランザクション開始
    session = common_repository.create_session()
    # user_screen_nameからuser_idを取得する
    user = twitter_user_repository.search_user(user_screen_name)
    user_id = user.twitter_user_id
    # 最古のツイートを取得する
    tweet = TwitterTweet
    oldest_tweet = session.query(tweet).filter(tweet.twitter_user_id == user_id).order_by(tweet.twitter_tweet_id).first()
    if oldest_tweet is None:
        session.close()
        return None
    else:
        oldest_tweet_id = oldest_tweet.twitter_tweet_id
        session.close()
        print('------------------- oldest_tweet_id:{}'.format(oldest_tweet_id))
        return oldest_tweet_id


def search_user_id(user_screen_name):
    # トランザクション開始
    session = common_repository.create_session()
    # user_screen_nameからuser_idを取得する
    user = twitter_user_repository.search_user(user_screen_name)
    user_id = user.twitter_user_id
    session.close()
    return user_id


# 削除処理
def delete_tweet_by_id(tweet_id):
    # トランザクション開始
    session = common_repository.create_session()
    # 削除処理
    row = session.query(TwitterTweet).filter_by(tweet_id=tweet_id).one()
    session.delete(row)
    # 変更をコミット
    session.commit()
