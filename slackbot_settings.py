# coding=utf-8
import os

# ↓ Localの時は必要！Herokuではバッティングしてエラーになる
API_TOKEN = os.environ['SLACK_API_TOKEN']

PLUGINS = [
    "slackbot.plugins"
]
