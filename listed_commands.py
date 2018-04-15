import requests
import pytz
import datetime
import time
import json
import util


ERROR_MSG = "Что-то поломалось! :("


def get_string_week_number():
    initial_day = datetime.date(year=2018, month=2, day=9)
    initial_week_number = initial_day.isocalendar()[1]
    today = datetime.date.today()
    current_week = today.isocalendar()[1] - initial_week_number
    first_day_of_current_week = datetime.datetime.strptime("{}-W{}".format(initial_day.year, current_week + initial_week_number) + '-1', "%Y-W%W-%w")
    return "{} -> {}\nУчебная неделя: {}".format(datetime.datetime.strftime(first_day_of_current_week, "%d.%m.%Y"),
                                                 datetime.datetime.strftime(first_day_of_current_week + datetime.timedelta(days=6), "%d.%m.%Y"),
                                                 current_week + 1)


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


def get_string_calendar(maximum=5):
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


def get_string_nearest_ctf():
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


def get_string_current_info():
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


def get_string_current_time():
    utc_time = datetime.datetime.now(tz=datetime.timezone.utc)
    msk_time = utc_time.astimezone(pytz.timezone("Europe/Moscow"))
    pst_time = utc_time.astimezone(pytz.timezone("PST8PDT"))

    out_format = "{calendar}\n{pst}\n{utc}\n{msk}\n"
    time_format = "%Z: %a %H:%M:%S (%z)\n(%I:%M %p)"

    return out_format.format(calendar=utc_time.strftime("UTC date: %d/%m/%Y (%A)"),
                             pst=pst_time.strftime(time_format),
                             utc=utc_time.strftime(time_format),
                             msk=msk_time.strftime(time_format))


def get_string_temperature():
    r = requests.get("https://gradus.melda.ru/data.json")
    out = r.json()['timestamp'] + "\n"
    out += r.json()['temperature']
    return out.strip()


def get_string_help():
    return \
"""
💎 kksCTF bot v2.0 💎:
/help - Показать это меню
---
/calendar - Показать календарь CTF 🗓
/chef - Универсальный армейский кибер-нож 🔪
/current - Информация о текущей CTF 🔛
/nearest - Информация о ближайшей CTF 🔜
/shrug - ¯\\_(ツ)_/¯
/time - Текущее время (PST, UTC, MSK) ⏱
/temp - Температура на улице 🌡
/week - Текущая учебная неделя 📅
---
Мои исходники: https://github.com/kksctf/bot ;)
"""


available = {
    "/help": get_string_help,
    "/week": get_string_week_number,
    "/current": get_string_current_info,
    "/time": get_string_current_time,
    "/nearest": get_string_nearest_ctf,
    "/temp": get_string_temperature,
    "/chef": lambda: "https://gchq.github.io/CyberChef/",
    "/shrug": lambda: "¯\\_(ツ)_/¯",
    "/calendar": get_string_calendar
}
