# Development

Note: For development, you usually want to have installed the app in edit mode
`pip install -e .`.

To run a development server locally (NOT for production):

```bash
source venv/bin/activate
export WXFS_DSN=<wxfs dsn>
export FLASK_APP=wxfs.wsgi
export FLASK_ENV=development
flask run
```

Note: `<wxfs dsn>`. See [Configuration](configuration.md) for details.
