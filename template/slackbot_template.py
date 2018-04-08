from slackbot.bot import default_reply
from slackbot.bot import respond_to
from service import slackbot_service


@respond_to('coinScreenD')
def coingecko_screenshot_dashboard(message):
    slackbot_service.coingecko_screenshot_dashboard(message)


@respond_to('searchTweet (.*)')
def post_top_tweet(message, word):
    slackbot_service.post_top_tweet(message, word)


@default_reply(matchstr='(.*)')
def talk(message, input):
    slackbot_service.dialogue_with_docomo_api(message, input)
