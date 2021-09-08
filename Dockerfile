FROM python:3.9-alpine
LABEL maintainer="Arun445"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /spending_app
WORKDIR /spending_app
COPY ./spending_app /spending_app

RUN adduser -D user
USER user