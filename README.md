# BioFarm-Monitor

Farm and herd management web app

## Installation

The installation requires `venv` and `pip` to download the required packages.
Before running the app, execute the following lines:

```
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements.txt
```

Before the first run, you have to clean the databases:

```
flask init_db
```

## Usage

Go to the project's top-level directory and run:

```
flask run
```
