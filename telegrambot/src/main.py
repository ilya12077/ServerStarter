import datetime
import html
import json
import os

import requests
from flask import Flask, request
from waitress import serve

from rcon import MCRcon
from tools import send_message, upload_photo, keyboards, check_port, upload_file, close_server, launch_server, is_easteregg, append_log, get_admins

app = Flask(__name__)

url = 'https://api.telegram.org/bot5570097300:AAHATJopuiSHBk8oN_uG3ty_95m2D5Q3Nzw/'
if os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
    path = '/etc/telegrambot/'
else:
    path = ''
with open(f'{path}names.json', 'r') as fl:
    ids = json.load(fl)


@app.route('/', methods=['GET', 'POST'])
def firewall():
    if request.method == "GET":
        return 'I\'m working'
    r = request.get_json()
    # write_json(r)  # answer.json
    if 'message' in r:
        user_id = str(r['message']['from']['id'])
        first_name = r['message']['from']['first_name']
        if 'text' in r['message']:
            if user_id in ids:
                pre_routine(r)
            else:
                upload_photo(user_id, f'{path}045iy8i1SO8.png')
                for admin in get_admins():
                    send_message(admin, f'Новый пользователь <code>{user_id}</code>({first_name}) пытался получить доступ к боту', keyboards(admin))
        else:
            send_message(user_id, 'Я понимаю только текст')
    return 'OK'


def pre_routine(r):
    global ids
    user_id = str(r['message']['from']['id'])
    first_name = r['message']['from']['first_name']
    msg = r['message']['text']
    # print(msg)
    if ids[user_id]['first_name'] != first_name:
        append_log(first_name, f'изменено имя пользователя {user_id} с {ids[user_id]["first_name"]} на {first_name}')
        ids[user_id]['first_name'] = first_name
        with open(f'{path}names.json', 'w') as f:
            json.dump(ids, f, indent=2)
    if user_id != '647372660':
        append_log(first_name, msg)
    if ids[user_id]['waiting']['is_waiting']:
        waiting_user_handler(r)
    else:
        main_handler(r)


def waiting_user_handler(r):
    global ids
    msg = r['message']['text']
    user_id = str(r['message']['from']['id'])
    first_name = r['message']['from']['first_name']
    reason = ids[user_id]['waiting']['params']['reason']
    if msg == 'Отмена':
        ids[user_id]['waiting']['is_waiting'] = False
        del ids[user_id]['waiting']['params']
        with open(f'{path}names.json', 'w') as f:
            json.dump(ids, f, indent=2)
        send_message(user_id, 'Действие отменено', keyboards(user_id))
        return None  # иначе дальше будет поиск по несущ. ключу и будет ошибка
    match reason:
        case 'send message to':
            if msg in list(ids[_id]['first_name'] for _id in ids):
                for _id in ids:
                    if ids[_id]['first_name'] == msg:
                        ids[user_id]['waiting']['params']['to_person'] = int(_id)
                        ids[user_id]['waiting']['params']['reason'] = 'what to send in message'
                        with open(f'{path}names.json', 'w') as f:
                            json.dump(ids, f, indent=2)
                        break

                data = {'keyboard': [[{'text': 'Отмена'}]],
                        'one_time_keyboard': True,
                        'resize_keyboard': True}
                send_message(user_id, 'Хорошо, а что отправляем?', data)
            else:
                send_message(user_id, 'Не знаю такого', keyboards(user_id))
                ids[user_id]['waiting']['is_waiting'] = False
                del ids[user_id]['waiting']['params']
                with open(f'{path}names.json', 'w') as f:
                    json.dump(ids, f, indent=2)
                send_message(user_id, 'Отправил', keyboards(user_id))

        case 'what to send in message':
            send_message(ids[user_id]['waiting']['params']['to_person'], f"Сообщение от {first_name}:")
            send_message(ids[user_id]['waiting']['params']['to_person'], msg, keyboards(user_id), spoiler=True)
            ids[user_id]['waiting']['is_waiting'] = False
            del ids[user_id]['waiting']['params']
            with open(f'{path}names.json', 'w') as f:
                json.dump(ids, f, indent=2)
            send_message(user_id, 'Отправил', keyboards(user_id))

        case 'allow user' | 'disallow user' | 'grant admin' | 'revoke admin':
            if msg.find('(') != -1 and msg.find('(') != -1:
                msg = msg[msg.index('(') + 1:msg.index(')')]  # берет userid из соо
            try:
                if int(msg) == 647372660:
                    send_message(user_id, 'Этот аккаунт защищен от изменений', keyboards(user_id))
                    append_log(first_name, 'Пытался изменить защищенную учетную запись')
                else:
                    send_message(user_id, change_user(user_id, msg, reason), keyboards(user_id))
            except ValueError:
                send_message(user_id, 'Неверный формат', keyboards(user_id))

            ids[user_id]['waiting']['is_waiting'] = False
            del ids[user_id]['waiting']['params']
            with open(f'{path}names.json', 'w') as f:
                json.dump(ids, f, indent=2)

        case 'close server':
            if msg == 'да':
                if not check_port(25565):
                    send_message(user_id, 'Сервер не запущен', keyboards(user_id))
                else:
                    if not check_port(1813):
                        send_message(user_id, 'Скрипт на пк не запущен, напиши в лс', keyboards(user_id))
                    else:
                        status_code = close_server(user_id, timeout=60)
                        if status_code == 200:
                            send_message(user_id, 'Сервер закроется через 60 секунд', keyboards(user_id))
                        elif status_code == 201:
                            send_message(user_id, 'Серв уже закрывается', keyboards(user_id))
                        else:
                            send_message(user_id, f'Что-то не сработало, напиши в лс ({status_code})', keyboards(user_id))
            else:
                send_message(user_id, f'Не выключаю', keyboards(user_id))
            ids[user_id]['waiting']['is_waiting'] = False
            del ids[user_id]['waiting']['params']
            with open(f'{path}names.json', 'w') as f:
                json.dump(ids, f, indent=2)

        case 'rcon command':
            try:
                with MCRcon(host="192.168.1.10", password="Homa1207", port=25575) as mcr:
                    result = mcr.command(msg)
                    if result == '':
                        result = '[OK]'
                    send_message(user_id, 'Ответ:', keyboards(user_id))
                    send_message(user_id, f'<pre>{html.escape(result)}</pre>', keyboards(user_id))
                    ids[user_id]['waiting']['is_waiting'] = False
                    del ids[user_id]['waiting']['params']
                    with open(f'{path}names.json', 'w') as f:
                        json.dump(ids, f, indent=2)
            except ConnectionRefusedError:
                send_message(user_id, 'Сервер не запущен', keyboards(user_id))


def change_user(user_id, user, action):
    global ids
    match action:
        case 'allow user':
            if user in ids:
                return 'Он уже добавлен'
            else:
                ids[user] = {'first_name': '#N/A', 'waiting': {'is_waiting': False}, 'is_admin': False}
                with open(f'{path}names.json', 'w') as f:
                    json.dump(ids, f, indent=2)
                append_log(ids[user_id]["first_name"], f'добавлен пользователь {user}')
                send_message(user, 'Вам был открыт доступ к боту. Начните: /start')
                return 'Добавил'
        case 'disallow user':
            if user_id == user:
                return 'https://life09.kz/ru/news/novosti-chestno-govorya/suicid-ne-vykhod-pochemu-voznikaet-zhelanie-pokonchit-zhizn'
            if user not in ids:
                return 'Пользователя нет в базе'
            else:
                append_log(ids[user_id]["first_name"], f'удален пользователь {ids[user]["first_name"]}({user})')
                send_message(user, 'Вам был закрыт доступ к боту')
                del ids[user]
                with open(f'{path}names.json', 'w') as f:
                    json.dump(ids, f, indent=2)
                return 'Удалил'

        case 'grant admin':
            if user not in ids:
                return 'Пользователя нет в базе'
            if ids[user]['is_admin']:
                return 'Он и так админ'
            else:
                ids[user]['is_admin'] = True
                with open(f'{path}names.json', 'w') as f:
                    json.dump(ids, f, indent=2)
                append_log(ids[user_id]["first_name"], f'пользователь {ids[user]["first_name"]}({user}) установлен админом')
                send_message(user, 'Поздравляю! Вы теперь админ', keyboards(user))
                return f'Пользователь установлен админом'
        case 'revoke admin':
            if user not in ids:
                return 'Пользователя нет в базе'
            if not ids[user]['is_admin']:
                return 'Он и так не админ'
            else:
                ids[user]['is_admin'] = False
                with open(f'{path}names.json', 'w') as f:
                    json.dump(ids, f, indent=2)
                append_log(ids[user_id]["first_name"], f'пользователь {ids[user]["first_name"]}({user}) удален из админов')
                send_message(user, 'У Вас забрали админку :(', keyboards(user_id))
                return f'Пользователь удален из админов'


def main_handler(r):
    global ids
    user_id = str(r['message']['from']['id'])
    first_name = r['message']['from']['first_name']

    msg = r['message']['text']
    if is_easteregg(r):
        return 'OK', 200

    match msg:
        case '/start':
            send_message(user_id, 'Чего желаешь?', keyboards(user_id))

        case '/info':
            if check_port(25565):
                send_message(user_id, 'Сервер запущен', keyboards(user_id))  #колво игроков
            else:
                send_message(user_id, 'Сервер выключен', keyboards(user_id))
            if not check_port(1813):
                send_message(user_id, 'Скрипт на пк не запущен, напиши в лс', keyboards(user_id))

        case '/launch':
            if check_port(25565):
                send_message(user_id, 'Сервер уже запущен', keyboards(user_id))
            else:
                if not check_port(1813):
                    send_message(user_id, 'Скрипт на пк не запущен, напиши в лс', keyboards(user_id))
                else:
                    was_it_launched = launch_server(user_id)
                    if was_it_launched is True:
                        send_message(user_id, 'Запускаю', keyboards(user_id))
                    elif was_it_launched is False:
                        send_message(user_id, 'Комп выключен, напиши в лс', keyboards(user_id))
                    elif was_it_launched == 'busy':
                        send_message(user_id, 'Серв уже запускается', keyboards(user_id))
                    else:
                        send_message(user_id, f'Что-то не сработало, напиши в лс ({was_it_launched})', keyboards(user_id))

        case '/close':
            if not check_port(25565):
                send_message(user_id, 'Сервер не запущен', keyboards(user_id))
            else:
                if not check_port(1813):
                    send_message(user_id, 'Скрипт на пк не запущен, напиши в лс', keyboards(user_id))
                else:
                    with MCRcon(host="192.168.1.10", password="Homa1207", port=25575) as mcr:
                        player = mcr.command("/list")
                        list_players = player[player.index(':') + 1:]
                        players = int(player[9:11])
                        if players > 0:
                            if user_id in get_admins():
                                data = {'keyboard': [[{'text': 'да'}, {'text': 'НЕТ'}]],
                                        'one_time_keyboard': True,
                                        'resize_keyboard': True}
                                send_message(user_id, f'Сейчас на сервере {players} игроков: <i>{list_players}</i>. Выключить?', data)
                                ids[user_id]['waiting']['is_waiting'] = True
                                ids[user_id]['waiting']['params'] = {'reason': 'close server'}
                                with open(f'{path}names.json', 'w') as f:
                                    json.dump(ids, f, indent=2)
                                return False
                            else:
                                send_message(user_id, f'Сейчас на сервере {players} игроков: <i>{list_players}</i>, не могу выключить. Попросите администратора выключить сервер', keyboards(user_id))
                                return False
                        else:
                            status_code = close_server(user_id, timeout=5)
                    if status_code == 200:
                        send_message(user_id, 'Сервер закроется через 5 секунд', keyboards(user_id))
                    elif status_code == 201:
                        send_message(user_id, 'Серв уже закрывается', keyboards(user_id))
                    else:
                        send_message(user_id, f'Что-то не сработало, напиши в лс ({status_code})', keyboards(user_id))

        case '/logs' if ids[user_id]['is_admin']:
            with open(f'{path}log.txt', 'r', encoding='cp1251') as f:
                log = f.read()
                if len(log) <= 4096:
                    send_body = {
                        'chat_id': user_id,
                        'text': log,
                        'reply_markup': keyboards(user_id)
                    }
                    requests.post(url + 'sendMessage', json=send_body)
                else:
                    upload_file(user_id, 'log.txt')

        case '/clear_logs' if ids[user_id]['is_admin']:
            with open(f'{path}log.txt', 'w', encoding='cp1251') as f:
                f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {first_name}: *очистил логи*' + '\n')
                send_message(user_id, 'Очистил логи', keyboards(user_id))

            with open(f'{path}log.txt', 'r', encoding='cp1251') as f:
                log = f.read()
                send_body = {
                    'chat_id': user_id,
                    'text': log,
                    'reply_markup': keyboards(user_id)
                }
                requests.post(url + 'sendMessage', json=send_body)

        case '/rcon' if ids[user_id]['is_admin']:
            if check_port(25565):
                data = {'keyboard': [[{'text': 'Отмена'}]],
                        'one_time_keyboard': True,
                        'resize_keyboard': True}
                send_message(user_id, 'Какую команду отправить на сервер?', data)

                ids[user_id]['waiting']['is_waiting'] = True
                ids[user_id]['waiting']['params'] = {'reason': 'rcon command'}
                with open(f'{path}names.json', 'w') as f:
                    json.dump(ids, f, indent=2)
            else:
                send_message(user_id, 'Сервер выключен', keyboards(user_id))

        case 'Админ панель' if ids[user_id]['is_admin']:
            data = {'keyboard': [[{'text': 'Удалить пользователя'}, {'text': 'Добавить пользователя'}],
                                 [{'text': 'Убрать админку'}, {'text': 'Добавить админку'}],
                                 [{'text': '/clear_logs'}, {'text': '/logs'}],
                                 [{'text': 'Главное меню'}, {'text': '/rcon'}]],
                    'one_time_keyboard': True,
                    'resize_keyboard': True}
            send_message(user_id, 'Перехожу в админ панель', data)

        case 'Добавить пользователя' if ids[user_id]['is_admin']:
            data = {'keyboard': [[{'text': 'Отмена'}]],
                    'one_time_keyboard': True,
                    'resize_keyboard': True}
            send_message(user_id, 'Введите id нужного пользователя', data)

            ids[user_id]['waiting']['is_waiting'] = True
            ids[user_id]['waiting']['params'] = {'reason': 'allow user'}
            with open(f'{path}names.json', 'w') as f:
                json.dump(ids, f, indent=2)

        case 'Удалить пользователя' if ids[user_id]['is_admin']:
            data = {'keyboard': [[{'text': f"{ids[_id]['first_name']}({_id})"} for _id in ids],
                                 [{'text': 'Отмена'}]],
                    'one_time_keyboard': True,
                    'resize_keyboard': True}
            send_message(user_id, 'Выберите нужного пользователя', data)

            ids[user_id]['waiting']['is_waiting'] = True
            ids[user_id]['waiting']['params'] = {'reason': 'disallow user'}
            with open(f'{path}names.json', 'w') as f:
                json.dump(ids, f, indent=2)

        case 'Добавить админку' if ids[user_id]['is_admin']:
            data = {'keyboard': [[{'text': f"{ids[_id]['first_name']}({_id})"} for _id in ids if not ids[_id]['is_admin']],
                                 [{'text': 'Отмена'}]],
                    'one_time_keyboard': True,
                    'resize_keyboard': True}
            send_message(user_id, 'Выберите нужного пользователя', data)

            ids[user_id]['waiting']['is_waiting'] = True
            ids[user_id]['waiting']['params'] = {'reason': 'grant admin'}
            with open(f'{path}names.json', 'w') as f:
                json.dump(ids, f, indent=2)

        case 'Убрать админку' if ids[user_id]['is_admin']:
            data = {'keyboard': [[{'text': f"{ids[_id]['first_name']}({_id})"} for _id in ids if ids[_id]['is_admin']],
                                 [{'text': 'Отмена'}]],
                    'one_time_keyboard': True,
                    'resize_keyboard': True}
            send_message(user_id, 'Выберите нужного пользователя', data)

            ids[user_id]['waiting']['is_waiting'] = True
            ids[user_id]['waiting']['params'] = {'reason': 'revoke admin'}
            with open(f'{path}names.json', 'w') as f:
                json.dump(ids, f, indent=2)

        case 'Отправить сообщение':
            data = {'keyboard': [[{'text': ids[_id]['first_name']} for _id in ids],
                                 [{'text': 'Отмена'}]],
                    'one_time_keyboard': True,
                    'resize_keyboard': True}

            send_message(user_id, 'Кому отправляем?', data)

            ids[user_id]['waiting']['is_waiting'] = True
            ids[user_id]['waiting']['params'] = {'reason': 'send message to'}
            with open(f'{path}names.json', 'w') as f:
                json.dump(ids, f, indent=2)

        case 'Главное меню':
            send_message(user_id, 'Возврат в главное меню', keyboards(user_id))

        case _:
            send_message(user_id, 'Неизвестная команда', keyboards(user_id))


if __name__ == '__main__':
    if os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
        serve(app, host='0.0.0.0', port=8881, url_scheme='http')
    else:
        app.run(host='192.168.1.10', port=8881)
        # app.run(host='192.168.1.21', port=8881)

# https://api.telegram.org/bot5570097300:AAHATJopuiSHBk8oN_uG3ty_95m2D5Q3Nzw/getWebhookInfo
# https://api.telegram.org/bot5570097300:AAHATJopuiSHBk8oN_uG3ty_95m2D5Q3Nzw/setWebhook?url=telegram.bestserverever.com&drop_pending_updates=true
