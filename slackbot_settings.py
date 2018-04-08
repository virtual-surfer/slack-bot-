# coding=utf-8
import os

# ↓ Localの時は必要！Herokuではバッティングしてエラーになる
# API_TOKEN = os.environ['API_TOKEN']

PLUGINS = [
    "slackbot.plugins"
]
