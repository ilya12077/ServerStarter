FROM nginx:stable

RUN apt update && apt upgrade -y && apt install -y emacs &&\
    apt autoremove -y
COPY ./html /usr/share/nginx/html
COPY ./conf /etc/nginx

EXPOSE 80/tcp
CMD ["nginx", "-g", "daemon off;"]

