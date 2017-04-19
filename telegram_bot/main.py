#!/usr/bin/python3
import random

import requests
import json
import time
import datetime
import pickle
import logging
import sys

URL_TELEGRAM = "https://api.telegram.org/bot"
TOKEN = "284065983:AAGiyvMiLJRg0Q-g8ke-nZmG0T-rjEF3j_A"
BOT_NAME = "VideoST_bot"


def create_request_url(request):
    return URL_TELEGRAM + TOKEN + "/" + request


updates_url = create_request_url("getUpdates")
send_url = create_request_url("sendMessage")


def get_updates(offset=0):
    payload = {"offset": offset}
    response = requests.get(updates_url, json=payload)
    json_response = json.loads(response.text)

    if not json_response["ok"]:
        dump("so sorry, response updates: {}".format(json_response))

    return json_response["result"]


def send(chat_id, text):
    dump("send to chat_id = {}, text = {}".format(chat_id, text))
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(send_url, json=payload)
    json_response = json.loads(response.text)

    if "error_code" in json_response:
        dump("error SEND: {}".format(response.text))

        try:
            existing_chats.remove(chat_id)
        except:
            pass

        return -1
    else:
        dump("SEND: {}".format(response.text))

        if not json_response["ok"]:
            dump("so sorry, response: {}".format(json_response))

        return 0


def start_cmd(chat_id):
    dump("in start_cmd")
    global existing_chats
    send(chat_id, "Hi, I can make your video better")
    existing_chats.add(chat_id)


def stop_cmd(chat_id):
    global existing_chats

    dump("in stop_cmd")
    send(chat_id, "No, please :(")

    existing_chats.remove(chat_id)


def dump_users(*_):
    global last_dumped_time
    last_dumped_time = datetime.datetime.now()

    dump("dump users")
    with open("users.txt", "wb") as u:
        # pickle.dump(existing_chats, u)
        pickle.dump(last_update_id, u)
        pickle.dump(g_chat_id, u)


def load_users(*_):
    global existing_chats
    global last_update_id
    global g_chat_id

    dump("load_users")
    try:
        with open("users.txt", "rb") as u:
            existing_chats = pickle.load(u)
            last_update_id = pickle.load(u)
            g_chat_id = pickle.load(u)

            dump(existing_chats)
    except Exception as e:
        dump("users.txt doesn't exist")
        dump(e)


def setup_logger():
    global dump

    formatter = logging.Formatter('%(asctime)s (%(threadName)-10s) %(message)s', datefmt='%H:%M:%S')
    file_handler = logging.FileHandler("videoST.log", mode='w')
    file_handler.setFormatter(formatter)

    logger = logging.getLogger("videoST")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    dump = logger.debug


def duplicate_commands_with_bot_name():
    global commands
    new_commands = {}
    for name, cmd in commands.items():
        new_commands[name + "@" + BOT_NAME] = cmd

    commands.update(new_commands)


def shut_down(chat_id, *_):
    global proceed

    # for deleting recent shut_down request
    unused = get_updates(last_update_id)
    send(chat_id, "shut down :(")

    dump("shut_donw")
    dump_users()
    proceed = False

proceed = True
existing_chats = set()
last_update_id = 0
g_chat_id = 0
g_motivation_num = 0
last_dumped_time = datetime.datetime.now()

commands = {"/start": start_cmd,
            "/stop": stop_cmd,
            "/shut_down": shut_down
            }

if __name__ == "__main__":
    setup_logger()
    load_users()
    duplicate_commands_with_bot_name()

    while proceed:
        try:
            json_response = get_updates(last_update_id)

            for entry in json_response:
                msg = entry["message"]
                if "text" in msg:
                    dump("entry: {}".format(entry))
                    text = msg["text"]
                    g_chat_id = msg["chat"]["id"]
                    last_update_id = max(last_update_id, entry["update_id"] + 1)

                    if text in commands:
                        dump("command, chat_id: {} {}".format(text, g_chat_id))
                        commands[text](g_chat_id)

            time.sleep(100)

            cur = datetime.datetime.now()

            if cur - last_dumped_time > datetime.timedelta(minutes=1):
                dump_users()
        except Exception as e:
            dump_users()
            dump(e)
