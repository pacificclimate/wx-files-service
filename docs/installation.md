# Installation

This project is installed and built with [poetry](https://python-poetry.org/).

The procedure is straightforward: Clone the project and install it.

```bash
$ git clone https://github.com/pacificclimate/wx-files-service
$ cd wx-files-service
$ poetry install --with=dev
```

The final step (`poetry install --with=dev`) installs this project with development dependencies like `pytest`.
For production environments, use `poetry install`.
