#!/usr/bin/env bash
set -ex

# run flask app to
pipenv run pip install flask
export FLASK_APP=hello.py
pipenv run python -m flask run --host 0.0.0.0 --port 8000 &

pipenv run celery -A proco.taskapp worker -l INFO
