# coding=utf-8
import os

# ↓ Localの時は必要！Herokuではバッティングしてエラーになる
SLACKBOT_API_TOKEN = os.environ['SLACKBOT_API_TOKEN']

PLUGINS = [
    "slackbot.plugins"
]
