# coding=utf-8
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from entity.models import TwitterUser

# 環境変数からDB接続情報取得
MYSQL_USER = os.environ['MYSQL_USER']
MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']
MYSQL_HOST = os.environ['MYSQL_HOST']
MYSQL_DB = os.environ['MYSQL_DB']

# MySQL接続
engine = create_engine('mysql://{user}:{password}@{host}/{db}'
                       .format(user=MYSQL_USER, password=MYSQL_PASSWORD, host=MYSQL_HOST, db=MYSQL_DB),
                       encoding='utf-8', echo=False)

# トランザクション開始
Session = sessionmaker(bind=engine)
session = Session()

# user追加
test_user = TwitterUser(user_name='testマン', user_screen_name='testman', profile_image_link='test/link')
session.add(test_user)

# user複数追加
session.add_all([
    TwitterUser(user_name='taro', user_screen_name='taro', profile_image_link='taro/link'),
    TwitterUser(user_name='hanako', user_screen_name='hanako', profile_image_link='hanako/link'),
    TwitterUser(user_name='pochi', user_screen_name='pochi', profile_image_link='pochi/link')])

# 変更をコミット
session.commit()
