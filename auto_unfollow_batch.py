# coding=utf-8
from service.twitter import twitter_service
import random
from datetime import datetime


def unfollow(user_screen_name, max_count):
    twitter_service.unfollow(user_screen_name, max_count)


# 奇数日ならMax400人アンフォロー実行する
if datetime.now().day % 2 != 0:
    unfollow('virtual_techX', 400)
