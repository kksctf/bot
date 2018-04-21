import requests
import time

class TelegramBot:
    CONNECTION_LOST_TIMEOUT = 60

    def __init__(self, token, proxies=None):
        self.token = token
        self.url = f"https://api.telegram.org/bot{self.token}/"
        self.update_id = 0
        self.proxies = proxies
        self._check_token()

    def _check_token(self):
        r = requests.get(self.url + "getMe", proxies=self.proxies)

        if r.json()['ok'] == True:
            return True
        else:
            raise ValueError("Invalid token!")

    def get_messages(self):
        out = []
        try:
            r = requests.get(f"{self.url}getUpdates?offset={self.update_id}", timeout=self.CONNECTION_LOST_TIMEOUT, proxies=self.proxies).json()
        except requests.exceptions.RequestException as e:
            print(f"{int(time.time())} | Error while getting messages:", e)
            return out

        if r['ok'] and 'result' in r.keys():
            for i in r['result']:
                if 'text' in i['message'].keys():
                    out.append(i['message'])
                if i['update_id'] >= self.update_id:
                    self.update_id = i['update_id']+1
        return out

    def send_message(self, chat_id, text, parse_mode=''):
        try:
            r = requests.post(f"{self.url}sendMessage", 
                              data={'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode},
                              timeout=self.CONNECTION_LOST_TIMEOUT,
                              proxies=self.proxies)
        except requests.exceptions.RequestException as e:
            print(f"{int(time.time())} | Error while sending message:", e)
            return None

        return r
