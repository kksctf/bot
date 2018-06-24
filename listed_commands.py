import requests
import pytz
import datetime
import time
import json
import util
import threading


ERROR_MSG = "Что-то поломалось! :("


def get_string_week_number(**kwargs):
    return "Disabled until September 1st, 2018"
    """
    initial_day = datetime.date(year=2018, month=2, day=9)
    initial_week_number = initial_day.isocalendar()[1]
    today = datetime.date.today()
    current_week = today.isocalendar()[1] - initial_week_number
    first_day_of_current_week = datetime.datetime.strptime("{}-W{}".format(initial_day.year, current_week + initial_week_number) + '-1', "%Y-W%W-%w")
    return "{} -> {}\nУчебная неделя: {}".format(datetime.datetime.strftime(first_day_of_current_week, "%d.%m.%Y"),
                                                 datetime.datetime.strftime(first_day_of_current_week + datetime.timedelta(days=6), "%d.%m.%Y"),
                                                 current_week + 1)
    """


def ctf_to_str(ctf):
    date = datetime.datetime.utcfromtimestamp(ctf['start'])
    date += datetime.timedelta(hours=3)
    out = "{}:\n{}; {} hours\n{}\n{}\n"\
        .format(ctf['name'],
                date.strftime("%B %d, %Y; %H:%M MSK"),
                ctf['duration'],
                ctf['type'],
                ctf['link'])
    return out


def get_string_calendar(maximum=5, **kwargs):
    out = []
    count = 0
    settings = util.load_settings()
    with open(settings['calendar_file']) as fin:
        data = json.load(fin)
        for ctf in sorted(data['ctfs'], key=lambda x: x['start']):
            if ctf['start'] > datetime.datetime.now().timestamp():
                count += 1
                out.append(ctf_to_str(ctf))
                if count >= maximum:
                    break

    if len(out) == 0:
        out.append("Calendar is empty")

    return "\n\n".join(out)


def get_string_nearest_ctf(**kwargs):
    settings = util.load_settings()
    out = ""
    with open(settings['calendar_file'], "r") as fin:
        data = json.load(fin)
        ctf = max(data['ctfs'], key=lambda x: x['start'])
        for i in data['ctfs']:
            if datetime.datetime.now() < datetime.datetime.fromtimestamp(i['start']) < datetime.datetime.fromtimestamp(ctf['start']):
                ctf = i

        start_time = datetime.datetime.fromtimestamp(ctf['start'])
        now_time = datetime.datetime.now()
        if now_time < start_time:
            out += ctf_to_str(ctf)
            delta_time = datetime.datetime.utcfromtimestamp((start_time - now_time).total_seconds())
            out += "> Time before: {}{:02d}:{:02d}:{:02d}\n".format(str(delta_time.day-1) + "d " if delta_time.day > 1 else "",
                                                                    delta_time.hour,
                                                                    delta_time.minute,
                                                                    delta_time.second)

    if out == "":
        out = "Not found."

    return out


def get_string_current_info(**kwargs):
    out = ""
    with open("ctf.json", "r") as fin:
        data = json.load(fin)
        for ctf in data['ctfs']:
            start_time = datetime.datetime.fromtimestamp(ctf['start'])
            end_time = datetime.datetime.fromtimestamp(ctf['start']) + datetime.timedelta(hours=ctf['duration'])
            now_time = datetime.datetime.now()
            if start_time < now_time < end_time:
                out += ctf_to_str(ctf)
                delta_time = datetime.datetime.utcfromtimestamp((end_time-now_time).total_seconds())
                out += "> Time left: {}{:02d}:{:02d}:{:02d}\n".format(str(delta_time.day-1) + "d " if delta_time.day > 1 else "",
                                                                      delta_time.hour,
                                                                      delta_time.minute,
                                                                      delta_time.second)
    if out == "":
        out = "No CTFs found"
    return out


def get_string_current_time(**kwargs):
    utc_time = datetime.datetime.now(tz=datetime.timezone.utc)
    msk_time = utc_time.astimezone(pytz.timezone("Europe/Moscow"))
    pst_time = utc_time.astimezone(pytz.timezone("PST8PDT"))

    out_format = "{calendar}\n{pst}\n{utc}\n{msk}\n"
    time_format = "%Z: %a %H:%M:%S (%z)\n(%I:%M %p)"

    return out_format.format(calendar=utc_time.strftime("UTC date: %d/%m/%Y (%A)"),
                             pst=pst_time.strftime(time_format),
                             utc=utc_time.strftime(time_format),
                             msk=msk_time.strftime(time_format))


class RatingGetter:
    def __init__(self, t):
        self.t = t
        self.last_response = 0
        self.last_rating = ""
        self.teams = util.load_settings()["ctftime_team_chat_ids"]["-1001190162920"]
        print("Rating getter initialized!")

    def get(self):
        if time.time() - self.last_response < self.t:
            return self.last_rating
        self.last_response = int(time.time())

        results = []
        for i in self.teams:
            results.append(ctftime_tools.get_tuple_ctftime_rating(i))
        results = sorted(results, key=lambda x: x[0])

        self.last_rating = "Last update: " + time.strftime("%H:%M:%S\n")
        self.last_rating += "\n\n".join([f">> {x[1]} <<\n2018 place: {x[0]}\nPoints: {x[2]}\nlink: https://ctftime.org/team/{x[3]}" for x in results])
        return self.last_rating


rating = RatingGetter(60*60)
def get_string_rating(**kwargs):
    return rating.get()


class TemperatureGetter:
    def __init__(self, t):
        self.t = t
        self.temperatures = []
        self.last_time = ""
        self.hFunction = self._ask_temp
        self.hFunction()
        self.thread = threading.Timer(self.t, self.handle_function)
        print("Temperature getter initialized!")

    def handle_function(self):
        self.hFunction()
        self.thread = threading.Timer(self.t, self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()

    def _ask_temp(self):
        _melda_ok = True
        try:
            r = requests.get("https://gradus.melda.ru/data.json", timeout=3)
        except:
            _melda_ok = False
            try:
                r = requests.get("https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather.forecast%20where%20woeid%20in%20(select%20woeid%20from%20geo.places(1)%20where%20text%3D%22Moscow%2C%20RU%22)&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys", timeout=3)
            except:
                return
        if _melda_ok:
            self.temperatures.append(float(r.json()['temperature']))
            self.last_time = r.json()['timestamp']
        else:
            _temp = int(r.json()['query']['results']['channel']['item']['condition']['temp'])
            self.temperatures.append(round(((_temp - 32) * 5.0/9.0), 1))
            self.last_time = r.json()['query']['created'][11:16] + "UTC"

        if len(self.temperatures) > 10:
            del self.temperatures[0]

    def _ask_yahoo_emoji(self):
        # https://developer.yahoo.com/weather/documentation.html?guccounter=1#item
        self.code_to_emoji = {
            0: '🌪',
            1: '🌧',
            2: '🌪',
            3: '🌩',
            4: '🌩',
            5: '🌧🌨',
            6: '🌧🌨',
            7: '🌧🌨',
            8: '🌧',
            9: '🌧',
            10: '🌧',
            11: '🌧',
            12: '🌧',
            13: '🌨',
            14: '🌨',
            15: '🌨',
            16: '🌨',
            17: '☄',
            18: '🌧🌨',
            19: '🌫',
            20: '🌫',
            21: '🌫',
            22: '🌫',
            23: '💨',
            24: '💨',
            25: '❄',
            26: '☁',
            27: '☁',
            28: '☁',
            29: '⛅',
            30: '⛅',
            31: '🌚',
            32: '🌝',
            33: '🌚',
            34: '🌝',
            35: '🌧☄',
            36: '🔥',
            37: '🌩',
            38: '🌩',
            39: '🌩',
            40: '🌧',
            41: '🌨',
            42: '🌨',
            43: '🌨',
            44: '⛅',
            45: '⛈',
            46: '🌨',
            47: '⛈'
        }
        try:
            r = requests.get("https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather.forecast%20where%20woeid%20in%20(select%20woeid%20from%20geo.places(1)%20where%20text%3D%22Moscow%2C%20RU%22)&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys")
            condition_code = int(r.json()['query']['results']['channel']['item']['condition']['code'])
            out = self.code_to_emoji[condition_code]
            return out
        except:
            return ""

    def get(self):
        out = f"{self.last_time}"

        condition = self._ask_yahoo_emoji()
        if condition != '':
            out += " " + condition

        out += '\n'

        out += "-" if self.temperatures[-1] < 0 else "+"
        out += str(abs(self.temperatures[-1])) + "°C "

        return out.strip()


_temperature_getter = TemperatureGetter(15*60)
_temperature_getter.start()
def get_string_temperature(**kwargs):
    return _temperature_getter.get()


def get_string_chef(**kwargs):
    return "https://gchq.github.io/CyberChef/"


def get_string_shrug(**kwargs):
    return "¯\\_(ツ)_/¯"


def get_string_help():
    return """
💎 kksCTF bot v2.3.0g 💎
/help - Показать это меню
---
/calendar - Показать календарь CTF 🗓
/chef - Универсальный армейский кибер-нож 🔪
/current - Информация о текущей CTF 🔛
/nearest - Информация о ближайшей CTF 🔜
/rating - Рейтинг kks-команд 📈
/shrug - ¯\\_(ツ)_/¯
/time - Текущее время (PST, UTC, MSK) ⏱
/temp - Температура на улице 🌡
---
Мои исходники: https://github.com/kksctf/bot ;)
"""


available = {
    "/help": get_string_help,
    "/week": get_string_week_number,
    "/rating": get_string_rating,
    "/calendar": get_string_calendar,
    "/current": get_string_current_info,
    "/nearest": get_string_nearest_ctf,
    "/time": get_string_current_time,
    "/temp": get_string_temperature,
    "/chef": get_string_chef,
    "/shrug": get_string_shrug
}
