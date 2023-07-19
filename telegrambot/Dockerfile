FROM python:3.11-slim

RUN apt-get update && apt-get upgrade -y && apt-get install -y emacs &&\
    apt-get autoremove -y
	
# Install software 
RUN apt-get install -y git

# Copy over private key, and set permissions
# Warning! Anyone who gets their hands on this image will be able
# to retrieve this private key file from the corresponding image layer
ADD id_ed25519 /root/.ssh/id_ed25519
RUN chmod 700 /root/.ssh/id_ed25519

# Create known_hosts
RUN touch /root/.ssh/known_hosts
# Add bitbuckets key
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

# Clone the conf files into the docker container
RUN git clone git@github.com:ilya12077/ServerStarter-Bot.git
	
	
RUN cp -r ./ServerStarter-Bot/telegrambot/src /etc/telegrambot
RUN rm -r -f ./ServerStarter-Bot/

RUN pip install requests waitress flask

ENV AM_I_IN_A_DOCKER_CONTAINER Yes

CMD ["python", "/etc/telegrambot/main.py"]

