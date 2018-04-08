# coding=utf-8
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
        'place': '東京'
    }
    response = requests.post(
        url,
        data=json.dumps(data),
        headers=headers
    ).json()
    context[context_key] = response['context']
    return response
