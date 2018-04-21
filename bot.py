#!/usr/bin/env python3

import os
import sys
import telegram_bot
import time
import json
import util

listed_commands_imported = False
try:
    import listed_commands
    listed_commands_imported = True
except ModuleNotFoundError:
    listed_commands_imported = False

unlisted_commands_imported = False
try:
    import unlisted_commands
    unlisted_commands_imported = True
except ModuleNotFoundError:
    unlisted_commands_imported = False

listed_commands_avail = listed_commands.available if listed_commands_imported else None
unlisted_commands_avail = unlisted_commands.available if unlisted_commands_imported else None


def print_commands(load_flag, commands_dictionary, msg):
    print(msg)
    if load_flag:
        for i in sorted(commands_dictionary):
            print(i)
    else:
        print("Not loaded!")


def print_info_from_message(message):
    fmt = "{} | {} {} (@{}){}: {}"
    out = fmt.format(time.ctime(message['date']),
                     message['from']['first_name'],
                     message['from']['last_name'] if 'last_name' in message['from'].keys() else "",
                     message['from']['username'] if 'username' in message['from'].keys() else "",
                     (" in " + message['chat']['title']) if 'title' in message['chat'].keys() else "",
                     message['text'])
    print(out)


def check_command(bot, available_dict, message):
    text = message['text']
    at_location = text.find("@")
    if at_location != -1:
        text = text[0:at_location]

    for ac, af in available_dict.items():
        if ac in text:
            bot.send_message(message['chat']['id'], af())
            return True


def main(bot, settings):
    while True:
        messages = bot.get_messages()
        for m in messages:
            print_info_from_message(m)
            if not check_command(bot, listed_commands_avail, m):
                check_command(bot, unlisted_commands_avail, m)
        time.sleep(settings['request_timeout'])


if __name__ == '__main__':
    if not(sys.version_info.major >= 3 and sys.version_info.minor >= 6):
        print("Python 3.6+ required!")
        exit(1)

    print("Import listed:", listed_commands_imported)
    print("Import unlisted:", unlisted_commands_imported)

    print_commands(listed_commands_imported, listed_commands_avail, "Listed commands:")
    print_commands(unlisted_commands_imported, unlisted_commands_avail, "Unlisted commands:")

    settings = util.load_settings()

    bot_token = ""
    try:
        with open(settings['token_file']) as fin:
            bot_token = fin.read()
    except FileNotFoundError as e:
        print("Cannot start bot! Error: ", e)
        exit(1)
    except:
        exit(2)
    
    try:
        proxies = settings['proxies']
    except KeyError as e:
        proxies = None
        print("Proxy server isn't set!")

    bot = telegram_bot.TelegramBot(bot_token, proxies)

    main(bot, settings)
