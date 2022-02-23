# syntax=docker/dockerfile:1

FROM python:3.9.5-slim-buster

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP app.py
ENV FLASK_DEBUG 1

RUN apt-get update
RUN apt-get install -y postgresql postgresql-server-dev-all
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN apt-get install -y python3-dev
RUN apt-get install -y gcc
RUN pip install -r requirements.txt

COPY . .
