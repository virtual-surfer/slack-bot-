import os
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from entity import common_entity


Base = common_entity.prepare_base()


class TwitterFollow(Base):
    __tablename__ = 'twitter_follow'

    twitter_follow_id = Column(BigInteger, primary_key=True)
    friend_id = Column(BigInteger, nullable=False)
    follower_id = Column(BigInteger, nullable=False)
    delete_flg = Column(Boolean, default=False, nullable=False)
    auto_flg = Column(Boolean, default=True, nullable=False)
    ins_datetime = Column(DATETIME, default=datetime.now, nullable=False)
    upd_datetime = Column(DATETIME, default=datetime.now, nullable=False)
