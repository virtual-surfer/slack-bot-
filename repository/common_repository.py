# coding=utf-8
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# LocalのMySQL接続
# MYSQL_USER = os.environ['MYSQL_USER']
# MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']
# MYSQL_HOST = os.environ['MYSQL_HOST']
# MYSQL_DB = os.environ['MYSQL_DB']
# engine = create_engine('mysql://{user}:{password}@{host}/{db}'
#                        .format(user=MYSQL_USER, password=MYSQL_PASSWORD, host=MYSQL_HOST, db=MYSQL_DB),
#                        encoding='utf-8', echo=False)

# HerokuのMySQL接続
engine = create_engine(os.environ['CLEARDB_DATABASE_URL'], encoding='utf-8', echo=False)


def create_session():
    Session = sessionmaker(bind=engine)
    return Session()
