# Production

This section outlines how the backend and frontend services are deployed.

Note: The indexing database is hosted on a separate server and is not part of
a production deployment of the backend/frontend services. For details on
setting up an indexing database see 
[Creating and populating Wx-Files databases](database.md).

## Docker

The web service app is Dockerized. A Docker image named `pcic/wx-files-service`
is automatically built by 
[a GitHub action](../.github/workflows/docker-publish.yml).

A typical deployment of the frontend and backend is in `./docker`.
The most up to date deployment configuration will be found in the [portainer-deployment respository](https://github.com/pacificclimate/portainer-deployment).

## HTTP Server

We use the [uvicorn asgi server](https://www.uvicorn.org/) to run the service.

