# coding=utf-8
import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from service import docomo_dialogue_service
from service.twitter import twitter_service
from service.twitter import twitter_common_service


def dialogue_with_docomo_api(message, input):
    text = docomo_dialogue_service.create_response_with_context(input).get('utt')
    reply_on_slack(message, text)


def coingecko_screenshot_dashboard(message):
    # Coingeckoにログインするためのメアド、パスワードを取得して、ログインします。
    COING_EMAIL_ADDRESS = os.environ['COING_EMAIL_ADDRESS']
    COING_PASSWORD = os.environ['COING_PASSWORD']
    # driver = webdriver.PhantomJS(executable_path='./vendor/')
    driver = webdriver.PhantomJS()
    driver.get('https://www.coingecko.com/account/sign_in')
    input_element_email = driver.find_element_by_id('user_email')
    input_element_password = driver.find_element_by_id('user_password')
    send_button = driver.find_element_by_name('commit')
    input_element_email.send_keys(COING_EMAIL_ADDRESS)
    input_element_password.send_keys(COING_PASSWORD)
    send_button.click()

    # ページが完全に読み込まれるまでの時間を加味して最大5秒間待ち、スクリーンショットを保存して、画像をpost。
    message.send("ダッシュボード読み込み中...ちょっと待ってくだせえ...")
    driver.set_page_load_timeout(5)
    driver.save_screenshot('screenShot.png')
    post_file('general', './screenShot.png')


def post_top_tweet(message, word):

    search_comment = '「{}」でtweet検索するね...'.format(word)
    send_to_slack(message, search_comment)

    # twitterのアクセス情報
    api = twitter_common_service.prepare_twitter_api('virtual_techX')
    search_results = twitter_common_service.search_tweet(api, word, 'popular', 100)
    if len(search_results) == 0:
        send_to_slack(message, 'ツイート見つからなかったす。')
        return

    # いいね数の多い順のつぶやき一覧取得
    statuses = twitter_common_service.sort_by_favorite_count(search_results, True)
    # いいね数の多い5つのつぶやき辞書取得
    top_five_statuses_dictionary = twitter_common_service.select_statuses(statuses, 5)
    top_five_statuses = top_five_statuses_dictionary.values()
    # slackにポストする形式に整えた文章作成
    text = twitter_service.create_tweet_list_text(top_five_statuses)

    send_to_slack(message, text)


def send_to_slack(message, text):
    """
    Slackで呼び出されたチャンネル上でtext返信
    """
    message.send(text)


def reply_on_slack(message, text):
    """
    Slackでメッセージを送ってきたユーザーに対してメンションをつけてtext返信
    """
    message.reply(text)


def post_file(channel, file_path):
    """
    Slackの特定のチャンネルにファイルを送信する
    """
    url_slack_api = 'https://slack.com/api/files.upload'
    slack_api_params = {
        'token': os.environ['SLACKBOT_API_TOKEN'],
        'channels': channel
    }
    files = {'file': open(file_path, 'rb')}
    requests.post(url_slack_api, data=slack_api_params, files=files)


def post_text(channel, text):
    """
    Slackの特定のチャンネル(channel)にtextを送信する
    """
    url_slack_api = 'https://slack.com/api/chat.postMessage'
    slack_api_params = {
        'token': os.environ['SLACKBOT_API_TOKEN'],
        'channel': channel,
        'text': text,  # 投稿するテキスト
        'link_names': 1,  # メンションを有効にする
    }
    requests.post(url_slack_api, data=slack_api_params)


def post_text_with_icon(channel, text, name, icon):
    """
    Slackの特定のチャンネル(channel)にtextを送信する
    name: 投稿するユーザーの名前
    icon: 投稿するユーザーのアイコン画像
    """
    url_slack_api = 'https://slack.com/api/chat.postMessage'
    slack_api_params = {
        'token': os.environ['SLACKBOT_API_TOKEN'],
        'channel': channel,
        'text': text,  # 投稿するテキスト
        'username': name,  # 投稿のユーザー名
        'icon_emoji': icon,  # 投稿のプロフィール画像に入れる絵文字
        'link_names': 1,  # メンションを有効にする
    }
    requests.post(url_slack_api, data=slack_api_params)
