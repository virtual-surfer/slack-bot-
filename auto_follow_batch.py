# coding=utf-8
from service.twitter import twitter_service
import random
from datetime import datetime


def search_follow(user_screen_name, query, max_count):
    """
    指定したuser_screen_nameのユーザーで、queryで検索したツイッターユーザーをmax_count数フォローして、DBにフォローデータを登録する。
    """
    twitter_service.search_follow(user_screen_name, query, max_count)


word_list = ['エンジニア', 'engineer', 'プログラミング', 'python', 'ブログ', 'はてなブログ', '仮想通貨', 'ブロックチェーン',
             'crypt currency', 'テンセント', 'アリババ', 'Java', 'Google Apps Script', 'Mona', 'モナ', 'XEM', 'NEM']

# 偶数日ならMax300人フォロー実行する
if datetime.now().day % 2 == 0:
    search_follow('virtual_techX', random.choice(word_list), 300)
