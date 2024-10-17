# Development

Note: For development, you usually want to have installed the app in edit mode
`poetry install --with=dev`.

To run a development server locally (NOT for production):

```bash 
export WXFS_DSN=<wxfs dsn>
export FLASK_APP=wxfs.asgi
export FLASK_ENV=development
poetry run uvicorn wxfs.asgi:connexion_app
```

Note: `<wxfs dsn>`. See [Configuration](configuration.md) for details.
