import datetime
import html
import json
import os
import socket

import requests

url = 'https://api.telegram.org/bot5570097300:AAHATJopuiSHBk8oN_uG3ty_95m2D5Q3Nzw/'
if os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
    path = '/etc/telegrambot/'
else:
    path = ''
with open(f'{path}names.json', 'r') as fl:
    ids = json.load(fl)


def keyboards(user):
    global ids
    if ids[user]['is_admin']:
        return {'keyboard': [[{'text': '/info'}, {'text': 'Админ панель'}],
                             [{'text': 'Отправить сообщение'}],
                             [{'text': '/launch'}, {'text': '/close'}]],
                'resize_keyboard': True}
    else:
        return {'keyboard': [[{'text': '/info'}],
                             [{'text': 'Отправить сообщение'}],
                             [{'text': '/launch'}, {'text': '/close'}]],
                'resize_keyboard': True}


def send_message(chat_id: int | str, message, keyboard=None, spoiler=False):
    if spoiler:
        message = f'<tg-spoiler>{message}</tg-spoiler>'
    if keyboard is None:
        send_body = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
    else:
        send_body = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML',
            'reply_markup': keyboard
        }
    r = requests.post(url + 'sendMessage', json=send_body)
    if r.status_code == 400:
        send_message(chat_id, html.escape(message), keyboard, spoiler)


def upload_photo(chat_id, file):
    files = {
        'photo': open(file, 'rb')
    }

    requests.post(f'{url}sendPhoto?chat_id={chat_id}', files=files)


def upload_file(chat_id, file):
    files = {
        'document': open(file, 'rb')
    }
    requests.post(f'{url}sendDocument?chat_id={chat_id}', files=files)


def upload_video(chat_id, file, caption=''):
    files = {
        'video': open(file, 'rb')
    }
    requests.post(f'{url}sendVideo?chat_id={chat_id}&caption={caption}', files=files)


def write_json(data):
    with open(f'{path}answer.json', 'w') as f:
        json.dump(data, f, indent=2)


def get_size(start_path='.'):
    total_size = 0
    for dir_path, dir_names, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dir_path, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return f'{total_size // 1024 // 1024 / 1024:.{2}} GBytes'


def append_log(user, msg):
    with open(f'{path}log.txt', 'a', encoding='cp1251') as f:
        try:
            f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {user}: {msg}' + '\n')
        except Exception as e:
            f.write(f'Exception {e}' + '\n')


def is_easteregg(r):
    user_id = r['message']['from']['id']
    msg = r['message']['text']
    if 'наркотик?' in msg:
        send_message(user_id, 'да, очень наркотический наркотик', keyboards(user_id))
        return True

    # noinspection SpellCheckingInspection
    if 'наркот' in msg:
        send_message(user_id, 'https://www.youtube.com/watch?v=nAlv9BF_W7w', keyboards(user_id))
        return True
    return False


def get_admins() -> list:
    with open(f'{path}names.json', 'r') as f:
        _ids = json.load(f)
        result = []
        for userid in _ids:
            if _ids[userid]['is_admin']:
                result.append(userid)
    return result


def check_port(port, host='192.168.1.10'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    return True if result == 0 else False


def launch_server(chat_id):
    status_code = requests.get(f'http://192.168.1.10:1813/server?issueid={chat_id}&action=launch').status_code
    if status_code == 200:
        return True
    elif status_code == 201:
        return 'busy'
    else:
        return status_code


def close_server(user_id, timeout=0):
    status_code = requests.get(f'http://192.168.1.10:1813/server?issueid={user_id}&action=close&timeout={timeout}').status_code
    return status_code
