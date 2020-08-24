# Wx Files Service

Metadata and data service for Wx Files. 
Main client is the Wx Files App, but this service stands independent of 
that app.

## Summary

This microservice provides 

- metadata describing the available weather files
- contents of the available weather files (as file downloads)

## Installation

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
