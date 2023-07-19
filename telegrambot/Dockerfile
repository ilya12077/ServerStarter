FROM python:3.11-slim

RUN apt-get update && apt-get upgrade -y && apt-get install -y emacs &&\
    apt-get autoremove -y
	
# Install software 
RUN apt-get install -y git

# Copy over private key, and set permissions
# Warning! Anyone who gets their hands on this image will be able
# to retrieve this private key file from the corresponding image layer
RUN echo "LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUFNd0FBQUF0emMyZ3RaVwpReU5UVXhPUUFBQUNEcXd6dDdJQjBmakphM2RVU1IrOXppRS9BejM4TkxVcVV0bjM5YUNLTHYwQUFBQUtETXMyN2d6TE51CjRBQUFBQXR6YzJndFpXUXlOVFV4T1FBQUFDRHF3enQ3SUIwZmpKYTNkVVNSKzl6aUUvQXozOE5MVXFVdG4zOWFDS0x2MEEKQUFBRURWeloySk9VbUp6V2FFcGZENnZ0b2Y2WlhhZmJ0cnV6OWZWMlBkMmpDTmlPckRPM3NnSFIrTWxyZDFSSkg3M09JVAo4RFBmdzB0U3BTMmZmMW9Jb3UvUUFBQUFGbTF5TG1sc2VXRXVNVEl3TjBCbmJXRnBiQzVqYjIwQkFnTUVCUVlICi0tLS0tRU5EIE9QRU5TU0ggUFJJVkFURSBLRVktLS0tLQo=" | openssl base64 -A -d > /root/.ssh/id_ed25519
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

