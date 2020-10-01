# Postgres Test Database

This directory contains the scripts necessary to spin up a Postgres database 
for testing on (e.g., migrations), as described in 
[Postgres - Create a database on Docker](https://pcic.uvic.ca/confluence/display/CSG/Postgres#Postgres-Createadatabaseondocker).
This instance has no content apart from 2 empty databases, `wxfs` and `public`.

## Docker compose

A set of docker-compose files enables us to spin up the database easily:

```bash
docker-compose up -d
```

## "Raw" docker

```bash
docker run -d -e POSTGRES_PASSWORD=postgres -p 30599:5432 -v ./tests/postgres-test-db:/docker-entrypoint-initdb.d --name wxfs docker-registry01.pcic.uvic.ca:5000/pcic/postgres_10.5_en_ca:latest -c 'listen_addresses=0.0.0.0'
```