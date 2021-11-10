# Wx Files Service

Metadata and data service for Wx Files. 
Main client is the Wx Files App, but this service stands independent of 
that app.

## Summary

This microservice provides 

- metadata describing the available weather files
- contents of the available weather files (as file downloads)

## Installation

It is best practice to install using a virtual environment.
Current recommended practice for Python3.3+ to use the 
[builtin `venv` module](https://docs.python.org/3/library/venv.html).
(Alternatively, `virtualenv` can still be used but it has shortcomings 
that are corrected in `venv`.)
See 
[Creating Virtual Environments](https://packaging.python.org/installing/#creating-virtual-environments) for an
overview of these tools.

```bash
$ git clone https://github.com/pacificclimate/wx-files-service
$ cd wx-files-service
$ python3 -m venv venv
$ source venv/bin/activate
(venv)$ pip install -U pip
(venv)$ pip install -i https://pypi.pacificclimate.org/simple/ \
    -r requirements.txt -r test_requirements.txt
(venv)$ pip install -e .
```

## Docker

The service API is, of course, Dockerized. To build the Docker image locally:

```
docker build -t wx-files-service .
```

## Run the service

### Locally

To run a dev server locally:

```bash
source venv/bin/activate
export FLASK_APP=wxfs.wsgi
export FLASK_ENV=development
flask run
```

### In a docker container

See `docker-compose.yaml` for an example.

## API design

### Data model

Since the API design reflects the data model, it helps to have a clear picture
of it. The following is a terrible ASCII rendering of the data model in UML:

Station (1)-------------(*) File
                              ^
                              |
                              +--- WxFile
                              |
                              +--- SummaryFile

Station:
    name
    unique id
    location (lat, lon)
    ...
    
File
    contentUri
    fileType: WxFile | SummaryFile
    
WxFile
    ... metadata describing a weather file ...
    
SummaryFile
    ... metadata describing a summary file ...
    

### Overview

We follow RESTful design principles in this microservice.

Specifically, we use the common collection pattern in its RESTful expression.

Overall API design is simple, since the content to be served is simple. 
In outline, the endpoints are:

- `/stations`: Collection of metadata objects, each describing a single
    station. Metadata includes name, location, collection of metadata
    for associated weather files.
    
- `/stations/{id}`: Metadata for a single station.

- `/files`: Collection of metadata objects, each describing a single
    file. Metadata for a file includes station.

- `/files/{id}`: Metadata for a single file.

- `/files/{id}/content`: Data content of a single file. For downloading a file.

### Releasing a new version

1. Increment `version` in `setup.py`.
2. Summarize the changes from the last version in `NEWS.md`.
3. Commit these changes, then tag the release, and push all to GitHub,
   including tag:

   ```bash
   git add setup.py NEWS.md
   git commit -m "Bump to version x.x.x"
   git tag -a -m "x.x.x" x.x.x
   git push --follow-tags
   ```
