FROM python:3.11-slim

RUN apt update && apt upgrade -y && apt install -y emacs &&\
    apt autoremove -y
COPY ./src /etc/telegrambot
RUN pip install requests waitress flask

ENV AM_I_IN_A_DOCKER_CONTAINER Yes

CMD ["python", "/etc/telegrambot/main.py"]
