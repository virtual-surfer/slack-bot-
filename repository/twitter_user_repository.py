# coding=utf-8
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from entity.twitter_user_entity import TwitterUser

# 環境変数からDB接続情報取得
MYSQL_USER = os.environ['MYSQL_USER']
MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']
MYSQL_HOST = os.environ['MYSQL_HOST']
MYSQL_DB = os.environ['MYSQL_DB']

# MySQL接続
engine = create_engine('mysql://{user}:{password}@{host}/{db}'
                       .format(user=MYSQL_USER, password=MYSQL_PASSWORD, host=MYSQL_HOST, db=MYSQL_DB),
                       encoding='utf-8', echo=False)


# 登録処理
def add_user(name, screen_name, image_link):
    # トランザクション開始
    Session = sessionmaker(bind=engine)
    session = Session()
    # user追加
    test_user = TwitterUser(user_name=name, user_screen_name=screen_name, profile_image_link=image_link)
    session.add(test_user)
    # 変更をコミット
    session.commit()


def add_users(users):
    # トランザクション開始
    Session = sessionmaker(bind=engine)
    session = Session()
    # bulkで一括user追加
    session.bulk_save_objects(
        [TwitterUser(user_name=user[0], user_screen_name=user[1], profile_image_link=user[2])
         for user in users], return_defaults=True)
    # 変更をコミット
    session.commit()


# 削除処理
def delete_user_by_id(twitter_id):
    # トランザクション開始
    Session = sessionmaker(bind=engine)
    session = Session()
    # 削除処理
    row = session.query(TwitterUser).filter_by(twitter_user_id=twitter_id).one()
    session.delete(row)
    # 変更をコミット
    session.commit()
