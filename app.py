# 運行以下程式需安裝模組: line-bot-sdk, flask, pyquery
# 安裝方式，輸入指令:
#1.啟動ngrok:  ./ngrok http 5001 
#2.將ngrok網址貼到 LINE Bot 的 Webhook Url
#3.啟動應用程式:
#python app.py
# pip install line-bot-sdk flask pyquery
from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    LocationMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

import os

from modules.reply import faq, menu
from modules.currency import get_exchange_table
table = get_exchange_table()
print(table)
app = Flask(__name__)

configuration = Configuration(access_token= os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))

@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_msg = event.message.text
        print("="*40)
        print(f"使用者傳入訊息了: {user_msg}")
        #print("event:",str[event])
        
        bot_msg = TextMessage(text = f"你剛才說了: {user_msg}")
        if user_msg in faq:
            bot_msg = faq[user_msg]
        elif user_msg in  ["選單","menu","home","m"]:
            bot_msg = menu
        elif user_msg in table:
            buy = table[user_msg]["buy"]
            sell = table[user_msg]["sell"]
            bot_msg = TextMessage(text = f"{user_msg} 買價:{buy} 賣價:{sell}")

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[bot_msg]
            )
        )


# 如果應用程式被執行執行
if __name__ == "__main__":
    print("[伺服器應用程式開始運行]")
    # 取得遠端環境使用的連接端口，若是在本機端測試則預設開啟於port=5001
    port = int(os.environ.get('PORT', 5001))
    print(f"[Flask即將運行於連接端口:{port}]")
    print(f"若在本地測試請輸入指令開啟測試通道: ./ngrok http {port} ")
    # 啟動應用程式
    # 本機測試使用127.0.0.1, debug=True
    # Heroku部署使用 0.0.0.0
    app.run(host="127.0.0.0", port=port, debug=False)
