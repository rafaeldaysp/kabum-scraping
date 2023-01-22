import requests
import json

def send_message(post):
    token = '5955496494:AAGfKkWJSIIbd2HO5l9sH4wa3FXSSUj-Xu4'
    chat_id = '-829725882'
    print('Enviando mensagem...')
    try:
        data = {"chat_id": chat_id, 
                "text": post}
        url = "https://api.telegram.org/bot5955496494:AAGfKkWJSIIbd2HO5l9sH4wa3FXSSUj-Xu4/sendMessage".format(token)
        requests.post(url, data)
    except Exception as e:
        print("Erro no sendMessage:", e)
