# coding=utf-8
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from repository import common_repository
from entity.twitter_user_entity import TwitterUser


# 取得処理
def search_user(user_screen_name):
    # トランザクション開始
    session = common_repository.create_session()
    # user_screen_nameからuserを取得する（存在しなければNoneを返す）
    user = TwitterUser
    target_user = session.query(user).filter(user.user_screen_name == user_screen_name).one_or_none()
    session.close()
    return target_user


# 登録処理
def add_user(user_id, screen_name, created_at):
    # トランザクション開始
    session = common_repository.create_session()
    # user追加
    user = TwitterUser(user_id=user_id, user_screen_name=screen_name, created_at=created_at)
    session.add(user)
    # 変更をコミット
    session.commit()


def add_users(users):
    # トランザクション開始
    session = common_repository.create_session()
    # bulkで一括user追加
    session.bulk_save_objects(
        [TwitterUser(user_id=user[0], user_screen_name=user[1], profile_image_link=user[2])
         for user in users], return_defaults=True)
    # 変更をコミット
    session.commit()


# 削除処理
def delete_user_by_id(twitter_id):
    # トランザクション開始
    session = common_repository.create_session()
    # 削除処理
    row = session.query(TwitterUser).filter_by(twitter_user_id=twitter_id).one()
    session.delete(row)
    # 変更をコミット
    session.commit()
