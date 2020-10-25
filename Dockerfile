FROM python:3.7-alpine
MAINTAINER Thomnas 5566

# tells python to run in unbuffered mode
# which is recommened when running python within Docker containers
ENV PYTHONUNBUFFERED 1

# copy from directory adjacemt to the Docker file 
COPY ./requirements.txt /requirements.txt
# use apckage manager apk add a package
# --no-cache means don't store the registry index on docker file
# because docker container for application has the smallest footprint possible 
RUN apk add --update --no-cache postgresql-client
# --virtual sets up an alias for our dependencies that we can use to easily remove all those dependencies later
# .tmp-build-deps basically temporary build dependencies
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev
# take /requirements.txt installs it using pip into the Docker image
RUN pip install -r /requirements.txt
# deletes the temporary requirements
RUN apk del .tmp-build-deps

# create a empty folder on docker
RUN mkdir /app 
# switches to that as the default directory
WORKDIR /app
# copy local mochine app folder to the Docker image app folder
COPY ./app /app

# create a user that is going to run our application using Docker
RUN adduser -D user
USER user