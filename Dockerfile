FROM python:3.7-alpine
MAINTAINER juawc

ENV PYTHONUNBUFFERED 1

COPY ./app/requirements.txt  /requirements.txt
RUN apk add --update --no-cache jpeg-dev mariadb-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc python3-dev musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
user user
