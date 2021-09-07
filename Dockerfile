FROM python:3.9-alpine
LABEL maintainer="Arun445"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /spending_app
WORKDIR /spending_app
COPY ./spending_app /spending_app

RUN adduser -D user
USER user