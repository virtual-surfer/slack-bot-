# coding=utf-8
from slackbot.bot import Bot
from slackbot.bot import respond_to
from slackbot.bot import default_reply
from selenium import webdriver
import tweepy
from selenium.webdriver.common.keys import Keys
import os
from PIL import Image
from io import BytesIO
import time
import requests
import json

url_slackapi = 'https://slack.com/api/files.upload'
context = {}


@default_reply(matchstr='(.*)')
def talk(message, input):
    global context
    url = 'https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue?APIKEY=' + os.environ['DOCOMO_API_KEY']
    headers = {'Content-type': 'application/json'}
    data = {
        'utt': input,
        'context': context.get(),
        'mode': 'dialog',
        'place': '東京'
    }
    response = requests.post(
        url,
        data=json.dumps(data),
        headers=headers
    ).json()
    context = response['context']
    message.reply(response.get('utt'))


@respond_to('coinScreenD')
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
    post_file('./screenShot.png')


def post_file(file_path):
    files = {'file': open(file_path, 'rb')}
    slackapi_params = {
        'token': os.environ['SLACKBOT_API_TOKEN'],
        'channels': 'general'
    }
    requests.post(url_slackapi, data=slackapi_params, files=files)


@respond_to('searchTweet (.*)')
def search_tweet(message, word):
    # twitterのアクセス情報
    auth = tweepy.OAuthHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])
    auth.set_access_token(os.environ['ACCESS_TOKEN'], os.environ['ACCESS_TOKEN_SECRET'])
    api = tweepy.API(auth)
    post_text = ''
    message.send('「' + word + '」でtweet検索するね...')
    search_results = api.search(q=word, lang='ja', result_type='recent', count=100)
    # 検索結果を辞書{検索結果, いいね数}に詰めていく
    result_dictionary = {}
    for result in search_results:
        user = result.user
        favorite_count = result.favorite_count
        tweet_link = 'https://twitter.com/' + user.screen_name + '/status/' + str(result.id)
        result_text = '\n' + user.name + '@(' + user.screen_name + ')\n' + result.text + '\n(' + str(
            favorite_count) + 'いいね)' + tweet_link + '\n'
        result_dictionary.setdefault(result_text, result.favorite_count)
    if len(result_dictionary) == 0:
        message.send('ツイート見つからなかったす。')
        return
    # いいね数が多い(valueの降順)ものからユーザー情報とつぶやき文章を取得
    loop_count = 0
    for k, v in sorted(result_dictionary.items(), key=lambda x: -x[1]):
        loop_count += 1
        post_text = post_text + '-------------------------------------------------------' + k
        # 5個分のツイートが取れたらループ中断
        if loop_count >= 5:
            break
    message.send(post_text)


def main():
    bot = Bot()
    bot.run()


if __name__ == '__main__':
    main()
