#!/usr/bin/env bash
set -ex

pipenv run python manage.py migrate
pipenv run python manage.py collectstatic --noinput
pipenv run gunicorn config.wsgi:application -b 0.0.0.0:8000 -w 8 --timeout=60
