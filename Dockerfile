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
RUN apk add --update --no-cache postgresql-client jpeg-dev
# --virtual sets up an alias for our dependencies that we can use to easily remove all those dependencies later
# .tmp-build-deps basically temporary build dependencies
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
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
# -p means make all of the subdirectories including the directory
# that we need e.t.c if the vol directory doesn't exist it will
# create vol web media directory
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/statuc
# create a user that is going to run our application using Docker
RUN adduser -D user
# sets the ownership of all the directory within the vol directory
# to our custom user -R means recursive
RUN chown -R user:user /vol/
# that the user can do everything so the owner can do everything
# with the directory can read execute from the directory
RUN chmod -R 755 /vol/web
USER user