# Wx Files Service

Metadata and data service for Wx Files. 
Main client is the Wx Files App, but this service stands independent of 
that app.

This microservice provides 

- metadata describing the available weather files
- contents of the available weather files (as file downloads)

## Documentation

- [Installation](docs/installation.md)
- [API](docs/api.md)
- [Configuration](docs/configuration.md)
- [Production deployment](docs/production.md)
- [Creating and populating Wx-Files databases](docs/database.md)
- [Development](docs/development.md)
- [Testing](docs/testing.md)

## Releasing

1. Increment `version` in `pyproject.toml`

2. Summarize the changes since the last version in `NEWS.md`

3. Commit these changes, then tag the release and push to github:

```bash
git add pyproject.toml NEWS.md
git commit -m "Bump to version x.x.x"
git tag -a -m "x.x.x" x.x.x
git push --follow-tags
```