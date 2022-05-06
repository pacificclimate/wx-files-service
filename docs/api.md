# API

## API overview

Note: The API is fully defined by an 
[OpenAPI spec](../wxfs/openapi/api-spec.yaml).

We follow RESTful design principles in this microservice.

Specifically, we use the common collection pattern in its RESTful expression.

Overall API design is simple, since the content to be served is simple.
In outline, the endpoints are:

- `/locations`: Collection of metadata objects, each describing a single
  location. Metadata includes name, geographic coordinates, and metadata
  for each associated weather file.

- `/locations/{id}`: Metadata for a single location.

- `/files`: Collection of metadata objects, each describing a single
  file. Metadata for a file includes station.

- `/files/{id}`: Metadata for a single file.

- `/files/{id}/content`: Data content of a single file. For downloading a file.

## Data model

Since the API design reflects the data model, it helps to have a clear picture
of it. The following is a terrible ASCII rendering of the data model in UML:

```text
Location (1)-------------(*) File
                              ^
                              |
                              +--- WxFile
                              |
                              +--- SummaryFile

Location:
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
```

For details, see the [ORM definition](../wxfs/database/__init__.py).
