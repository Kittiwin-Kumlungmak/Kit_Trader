from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, PostbackEvent, TextMessage, TextSendMessage,
    FlexSendMessage, QuickReply, QuickReplyButton, MessageAction,
    PostbackAction
)

from line_bot_config import *
from binance.client import Client
from config import *

app = Flask(__name__)

lineaccesstoken = channel_access_token 
line_bot_api = LineBotApi(lineaccesstoken) 
handler = WebhookHandler(line_secret_key) 

client = Client(bnb_api_key, bnb_api_secret)

@app.route('/webhook', methods= ['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    # user click rich menu
    if "My portfolio" in text:
        get_port_info(event)


def get_port_info(event):
    info = client.get_account()
    balances = info['balances']
    for asset in balances:
        if float(asset['free']) > 0:
            content = '{}:\t{}'.format(asset['asset'], asset['free'])

    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text= 'My Portfolio', contents= content)
        )

if __name__ == '__main__':
    app.run()