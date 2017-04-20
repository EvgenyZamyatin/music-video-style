#!/usr/bin/python3
import random

import requests
import json
import time
import datetime
import pickle
import logging
import sys
import urllib.request
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main_with_list_args as make_style

URL_TELEGRAM = "https://api.telegram.org/"
URL_TELEGRAM_BOT = URL_TELEGRAM + "bot"
TOKEN = "376252610:AAHQdNgobYzUjAjIGijmKsseCvTqHXjIj4Y"
BOT_NAME = "VideoST_bot"
DOWNLOAD_PATH = os.getcwd() + "/downloads/"


def create_request_url(request):
    return URL_TELEGRAM_BOT + TOKEN + "/" + request


updates_url = create_request_url("getUpdates")
send_message_url = create_request_url("sendMessage")
send_video_url = create_request_url("sendVideo")
get_file_url = create_request_url("getFile")
download_file_url = URL_TELEGRAM + "file/bot" + TOKEN + "/"  # + file_path


def get_updates(offset=0):
    payload = {"offset": offset}
    response = requests.get(updates_url, json=payload)
    json_response = json.loads(response.text)

    if not json_response["ok"]:
        dump("so sorry, response updates: {}".format(json_response))

    return json_response["result"]


def get_file(chat_id, file_id):
    dump("get_file from chat_id = {}".format(chat_id))
    payload = {"file_id": file_id}
    response = requests.post(get_file_url, json=payload)
    json_response = json.loads(response.text)

    dump("got responce: {}", json_response)

    res_path = None

    if "result" in json_response:
        result = json_response["result"]

        if "file_path" in result:
            file_path = result["file_path"]

            url_for_download_video = download_file_url + file_path

            _, video_extension = os.path.splitext(file_path)
            res_path = DOWNLOAD_PATH + str(chat_id) + video_extension

            dump("start downloading video from url: {}; to: {}".format(url_for_download_video, res_path))
            send_message(chat_id, "start downloading video: 10%")

            urllib.request.urlretrieve(url_for_download_video, res_path)

            dump("download completed")
            send_message(chat_id, "the download completed: 30%")
            send_message(chat_id, "start creating stylish video: 35%")

    return res_path


def send_message(chat_id, text):
    dump("send to chat_id = {}, text = {}".format(chat_id, text))
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(send_message_url, json=payload)
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


def send_video(chat_id, path_to_video):
    dump("start sending video to chat_id: {}, with path: {}".format(chat_id, path_to_video))
    with open(path_to_video, 'rb') as video_file:
        payload = {"video": video_file}
        send_url = "{}?chat_id={}".format(send_video_url, chat_id)
        response = requests.post(send_url, files=payload)
        json_response = json.loads(response.text)

        dump("video was sent: {}", json_response)


def start_cmd(chat_id):
    dump("in start_cmd")
    global existing_chats
    send_message(chat_id, "Hi, I can make your video better")
    existing_chats.add(chat_id)


def stop_cmd(chat_id):
    global existing_chats

    dump("in stop_cmd")
    send_message(chat_id, "No")

    existing_chats.remove(chat_id)


def dump_users(*_):
    global last_dumped_time
    last_dumped_time = datetime.datetime.now()

    dump("dump users")
    with open("users.txt", "wb") as u:
        pickle.dump(existing_chats, u)
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
    send_message(chat_id, "shut down :(")

    dump("shut_donw")
    dump_users()
    proceed = False


current_style = 'wave'


def handle_text(text, chat_id):
    global current_style
    if text in commands:
        dump("command, chat_id: {} {}".format(text, chat_id))
        commands[text](chat_id)
    if text == 'wave':
        current_style = 'wave'
    elif text == 'stained-glass':
        current_style = 'stained-glass'


def handle_doc(document, chat_id):
    dump("get doc: {}".format(document))

    res_path = get_file(chat_id, document["file_id"])

    if res_path is not None:
        base_name, extension = os.path.splitext(res_path)
        output_path = base_name + "_out" + extension

        args = ["--video=" + res_path,
                "--neural=" + "data/models/" + current_style,
                "--size=256",
                "--output=" + output_path]

        dump("make_style")
        make_style(args)

        send_message(chat_id, "stylish video was created: 70%")
        dump("stylish video was created")

        send_video(chat_id, output_path)


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

attributes_for_request = {"text": handle_text,
                          "document": handle_doc,
                          "video": handle_doc
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
                dump("got entry: {}".format(entry))

                g_chat_id = msg["chat"]["id"]
                last_update_id = max(last_update_id, entry["update_id"] + 1)

                for attr, handler in attributes_for_request.items():
                    if attr in msg:
                        handler(msg[attr], g_chat_id)
                        break

            time.sleep(1)

            cur = datetime.datetime.now()

            if cur - last_dumped_time > datetime.timedelta(minutes=1):
                dump_users()
        except Exception as e:
            dump_users()
            dump(e)
