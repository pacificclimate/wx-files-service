# Installation

In this project we still use a "manual" virtual environment installation 
procedure (as opposed to an all-in-one solution such as Pipenv).

The procedure is straightforward: Clone the project and install it.

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

The final step (`pip install -e .`) installs this project in development mode.
For production environments, use `pip install .`.
