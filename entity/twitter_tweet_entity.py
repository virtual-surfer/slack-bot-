import os
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from entity import common_entity


Base = common_entity.prepare_base()


class TwitterTweet(Base):
    __tablename__ = 'twitter_tweet'

    tweet_id = Column(BigInteger, primary_key=True)
    twitter_user_id = Column(BigInteger, ForeignKey('twitter_user.twitter_user_id'))
    twitter_tweet_id = Column(BigInteger, nullable=False)
    tweet_text = Column(String, nullable=False)
    tweet_datetime = Column(DATETIME, nullable=False)
    ins_datetime = Column(DATETIME, default=datetime.now, nullable=False)
    upd_datetime = Column(DATETIME, default=datetime.now, nullable=False)
