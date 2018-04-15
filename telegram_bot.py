import requests

class TelegramBot:
    CONNECTION_LOST_TIMEOUT = 60

    def __init__(self, token):
        self.token = token
        self.url = f"https://api.telegram.org/bot{self.token}/"
        self._check_token()
        self.update_id = 0

    def _check_token(self):
        if requests.get(self.url + "getMe").json()['ok'] == True:
            return True
        else:
            raise ValueError("Invalid token!")

    def get_messages(self):
        out = []
        r = requests.get(f"{self.url}getUpdates?offset={self.update_id}", timeout=self.CONNECTION_LOST_TIMEOUT).json()
        if r['ok'] and 'result' in r.keys():
            for i in r['result']:
                if 'text' in i['message'].keys():
                    out.append(i['message'])
                if i['update_id'] >= self.update_id:
                    self.update_id = i['update_id']+1
        return out

    def send_message(self, chat_id, text, parse_mode=''):
        r = requests.post(f"{self.url}sendMessage", 
                          data={'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode},
                          timeout=self.CONNECTION_LOST_TIMEOUT)
        return r

    def getme_telegram_api(self):
        return requests.get(self.url + "getMe").text
