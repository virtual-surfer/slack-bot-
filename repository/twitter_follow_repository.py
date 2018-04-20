# coding=utf-8
from repository import common_repository
from entity.twitter_follow_entity import TwitterFollow
from entity.twitter_user_entity import TwitterUser
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


# 取得処理
def search_follow(friend_id, follower_id):
    """
    friend_idのユーザーがfollower_idのユーザーをフォローテーブルを返す
    :param friend_id: フォローユーザー
    :param follower_id: 被フォローユーザー
    :return: フォローしているか否か True or False
    """
    # トランザクション開始
    session = common_repository.create_session()
    # 該当のfollowレコード取得。存在しなければNoneを返す
    follow = TwitterFollow
    follow_relation = session.query(follow).filter(and_(follow.friend_id == friend_id, follow.follower_id == follower_id)).one_or_none()
    session.close()
    return follow_relation


# 登録処理
def add_follow(friend_id, follower_id):
    """
    friend_idのユーザーがfollower_idのユーザーをフォローしたことを追加
    :param friend_id: フォローユーザー
    :param follower_id: 被フォローユーザー
    """
    # トランザクション開始
    session = common_repository.create_session()
    # followレコード登録
    follow = TwitterFollow(friend_id=friend_id, follower_id=follower_id)
    session.add(follow)
    # 変更をコミット
    session.commit()
    print('friend_id:{}がfollower_id:{}をフォローしたことをDB登録しました'.format(follow.friend_id, follow.follower_id))


# 更新処理
def update_follow_delete_flg(friend_id, follower_id):
    """
    friend_idのユーザーのfollower_idのユーザーフォローを外す(delete_flgをTrueに更新)
    :param friend_id: フォローユーザー
    :param follower_id: 被フォローユーザー
    """
    # トランザクション開始
    session = common_repository.create_session()
    # followレコード更新
    follow = TwitterFollow
    update(follow).where(follow.friend_id == friend_id and follow.follower_id == follower_id).values(delete_flg=True, upd_datetime=datetime.now())
    print('friend_id:{}がfollower_id:{}をフォローしたことを削除(delete_flgをTrue)に更新しました'.format(follow.friend_id, follow.follower_id))
    # 変更をコミット
    session.commit()
