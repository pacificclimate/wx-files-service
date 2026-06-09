# Copied from station-data-portal-backend, which in turn was
# adapted from weather-anomaly-data-service/Dockerfile and
# climate-explorer-backend/docker/Dockerfile.dev
# As always with docker, is there a better way to do this? Almost certainly.

FROM ubuntu:24.04

LABEL maintainer="Rod Glover <rglover@uvic.ca>"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get -yq install \
    curl \
    libpq-dev \
    pipx \
    python3 \
    python3-dev \
    postgresql-client && \
    rm -rf /var/lib/apt/lists/*

ADD . /app
WORKDIR /app

ENV PATH=/root/.local/bin:$PATH
RUN pipx install poetry
RUN poetry install

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/readyz || exit 1

ENV FLASK_APP=wxfs.asgi
ENV FLASK_ENV=development
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

CMD ["poetry", "run", "uvicorn", "--port", "8000", "--host", "0.0.0.0", "--reload", "wxfs.asgi:connexion_app"]
