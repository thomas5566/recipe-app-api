FROM python:3.7-alpine
MAINTAINER Thomnas 5566

# tells python to run in unbuffered mode
# which is recommened when running python within Docker containers
ENV PYTHONUNBUFFERED 1

# copy from directory adjacemt to the Docker file 
COPY ./requirements.txt /requirements.txt
# take /requirements.txt installs it using pip into the Docker image
RUN pip install -r /requirements.txt

# create a empty folder on docker
RUN mkdir /app 
# switches to that as the default directory
WORKDIR /app
# copy local mochine app folder to the Docker image app folder
COPY ./app /app

# create a user that is going to run our application using Docker
RUN adduser -D user
USER user