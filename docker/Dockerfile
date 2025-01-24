# Copied from station-data-portal-backend, which in turn was
# adapted from weather-anomaly-data-service/Dockerfile and
# climate-explorer-backend/docker/Dockerfile.dev
# As always with docker, is there a better way to do this? Almost certainly.

FROM ubuntu:22.04

MAINTAINER Rod Glover <rglover@uvic.ca>

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get -yq install \
        libpq-dev \
        python3 \
        python3-dev \
        python3-pip \
        postgresql-client \
	wget

ADD . /app
WORKDIR /app

RUN wget -O - https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH
RUN poetry install

EXPOSE 8000

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

CMD poetry run uvicorn --port 8000 --host 0.0.0.0 --reload --log-level trace wxfs.asgi:connexion_app
