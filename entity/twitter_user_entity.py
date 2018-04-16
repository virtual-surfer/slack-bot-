import os
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from entity import common_entity
from entity.twitter_tweet_entity import TwitterTweet
from entity.twitter_follow_entity import TwitterFollow

MYSQL_USER = os.environ['MYSQL_USER']
MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']
MYSQL_HOST = os.environ['MYSQL_HOST']
MYSQL_DB = os.environ['MYSQL_DB']

Base = common_entity.prepare_base()


class TwitterUser(Base):
    __tablename__ = 'twitter_user'

    twitter_user_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    user_screen_name = Column(String, nullable=False)
    created_at = Column(DATETIME, nullable=False)
    ins_datetime = Column(DATETIME, default=datetime.now, nullable=False)
    upd_datetime = Column(DATETIME, default=datetime.now, nullable=False)
    twitter_tweets = relationship("TwitterTweet", backref="twitter_user")
    # twitter_friend_follows = relationship("TwitterFollow", primaryjoin="twitter_user.twitter_user_id==TwitterFollow.friend_id")
    # twitter_follower_follows = relationship("TwitterFollow", primaryjoin="twitter_user.twitter_user_id==TwitterFollow.follower_id")
