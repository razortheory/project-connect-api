FROM python:3-stretch

# Install dependencies
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    build-essential \
    libcurl4-openssl-dev \
    libjpeg-dev \
    vim \
    ntp \
    libpq-dev
RUN apt-get install -y --no-install-recommends \
    git-core
RUN apt-get install -y --no-install-recommends \
    python3-dev \
    python-software-properties \
    python-setuptools
RUN apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    python-psycopg2

RUN pip install --upgrade \
    setuptools \
    pip \
    wheel

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /code
ENV VIRTUAL_ENV /usr/local

ARG REQUIREMENTS_FILE

ADD requirements /pip
RUN pip install -r /pip/${REQUIREMENTS_FILE}

ADD . /code/

WORKDIR /code/
