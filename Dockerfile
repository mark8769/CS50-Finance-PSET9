FROM python:3.12.2-bullseye
# Linux x86-64
# FROM --platform=linux/amd64 python:3.12.2-bullseye

# Create a new dir "app" at root of container, and switch to it.
WORKDIR app

# Copy all files from current dir to workdir in container
COPY [".", "."]

# Install all required python libraries
RUN ["pip3", "install", "-r", "requirements.txt"]

# Put your IEX API Key Here
ENV API_KEY=YOUR_API_KEY_HERE

# Run flask on port 8000 instead of default 5000
ENV FLASK_RUN_PORT=8000

# Denote to anyone that port 8000 is mean to be used
EXPOSE 8000

# CMD ["flask", "run"]
# https://www.freecodecamp.org/news/how-to-dockerize-a-flask-app/
# Have to pass --host even when though we use port mapping when using docker run (e.g -p 8000:8000)

# https://www.reddit.com/r/docker/comments/xwfm08/why_do_i_need_to_specify_host0000_when_running_a/
# By defaut flask will bind to localhost a.k.a. 127.0.0.1 
# which is only accessible to process running on the same machine. 
# Docker containers are virtually different machines so only a process running 
# within the same container would be able to reach it.
# What you want to do is to tell flask to be reachable using the public ip of 
# the container (public to the docker network). Since you don’t know which ip 
# address your container will be assigned within the docker subnetwork, 0.0.0.0 
# says to flask to accept incoming connections no matter the network adapter or the ip address.
CMD ["flask", "run", "--host=0.0.0.0"]