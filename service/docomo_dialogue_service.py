# coding=utf-8
import os
import requests
import json

context = {}


def create_response_with_context(input):
    global context
    context_key = 'context'
    url = 'https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue?APIKEY={}'.format(os.environ['DOCOMO_API_KEY'])
    headers = {'Content-type': 'application/json'}
    data = {
        'utt': input,
        'context': context.get(context_key, ''),
        'mode': 'dialog',
        "sex": "女",
        "nickname": "るかい",
        "nickname_y": "俺",
        "age": "18",
        "constellations": "双子座",
        'place': '東京'
    }
    response = requests.post(
        url,
        data=json.dumps(data),
        headers=headers
    ).json()
    context[context_key] = response['context']
    return response
