# coding=utf-8
from repository import common_repository
from entity.twitter_tweet_entity import TwitterTweet


# 登録処理
def add_tweet(user_id, tweet_id, text, datetime):
    # トランザクション開始
    session = common_repository.create_session()
    # user追加
    test_user = TwitterTweet(user_id=user_id, twitter_tweet_id=tweet_id, tweet_text=text, tweet_datetime=datetime)
    session.add(test_user)
    # 変更をコミット
    session.commit()


def add_tweets(tweets):
    # トランザクション開始
    session = common_repository.create_session()
    # bulkで一括user追加
    session.bulk_save_objects(
        [TwitterTweet(user_id=tweet[0], twitter_tweet_id=tweet[1], tweet_text=tweet[2], tweet_datetime=tweet[3])
         for tweet in tweets], return_defaults=True)
    # 変更をコミット
    session.commit()


# 削除処理
def delete_tweet_by_id(tweet_id):
    # トランザクション開始
    session = common_repository.create_session()
    # 削除処理
    row = session.query(TwitterTweet).filter_by(tweet_id=tweet_id).one()
    session.delete(row)
    # 変更をコミット
    session.commit()
