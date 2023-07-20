import fnmatch
import subprocess
import time
from threading import Thread

import requests
from flask import Flask, request
from mcrcon import MCRcon
from waitress import serve

app = Flask(__name__)
url = 'https://api.telegram.org/bot5570097300:AAHATJopuiSHBk8oN_uG3ty_95m2D5Q3Nzw/'


def upload_video(chat_id, file, caption=''):
    files = {
        'video': open(file, 'rb')
    }
    requests.post(f'{url}sendVideo?chat_id={chat_id}&caption={caption}', files=files)


def launch(issueid):
    global is_busy
    process = subprocess.Popen(
        r'cd C:\Users\mrily\Desktop\forgeserver && run.bat',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        encoding='cp1251',
        errors='replace'
    )
    while True:
        realtime_output = process.stdout.readline()
        if fnmatch.fnmatch(realtime_output, '*]: Done (*'):
            print(realtime_output.strip(), flush=True)
            is_busy = False
            upload_video(issueid, r'video_2022-08-21_19-16-23_2.mp4', 'И 5 секунд не прошло')
            break
        if realtime_output:
            print(realtime_output.strip(), flush=True)
        if realtime_output == '':
            break


def close(timeout: int):
    global is_busy
    timestamps = [60, 30, 10, 5, 4, 3, 2, 1]
    start_time = time.time()
    remaining_time = timeout
    with MCRcon(host="192.168.1.10", password="Homa1207", port=25575) as mcr:
        while remaining_time >= 0:
            if remaining_time in timestamps:
                timestamps.remove(remaining_time)
                print(f"WARNING: Server closes in {remaining_time} seconds")
                mcr.command(f"say WARNING: Server closes in {remaining_time} seconds")
            remaining_time = int(timeout - (time.time() - start_time))
            time.sleep(0.1)
        print('stop')
        mcr.command('stop')
        is_busy = False


@app.route('/server', methods=['GET'])
def main():
    global is_busy
    if not is_busy:
        userid = request.args.get('issueid')
        action = request.args.get('action')
        timeout = request.args.get('timeout')
        if not userid.isdigit():
            return 400
        match action:
            case 'launch':
                is_busy = True
                Thread(target=launch, args=[userid]).start()
                return 'k'
            case 'close':
                if not timeout.isdigit():
                    return 400
                is_busy = True
                Thread(target=close, args=[int(timeout)]).start()
                return 'k'
            case _:
                return 400
    else:
        return 'I\'m busy', 201


if __name__ == '__main__':
    is_busy = False
    serve(app, host='192.168.1.10', port=1813, url_scheme='http')
    # app.run(host='192.168.1.10', port=1813)
