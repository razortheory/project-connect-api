#!/usr/bin/env bash

set -ex

# tear down function
teardown()
{
    echo " Signal caught..."
    echo "Stopping celery multi gracefully..."

    # send shutdown signal to celery worker via `celery multi`
    # command must mirror some of `celery multi start` arguments
    pipenv run celery -A proco.taskapp multi stop 3 --logfile=/logs/celery-%n.log

    echo "Stopped celery multi..."
    echo "Stopping last waited process"
    kill -s TERM "$child" 2> /dev/null
    echo "Stopped last waited process. Exiting..."
    exit 1
}

stopcelery()
{
    # start trapping signals (docker sends `SIGTERM` for shutdown)
    trap teardown SIGINT SIGTERM

    sleep 3
    tail -F /logs/celery*.log &

    # capture process id of `tail` for tear down
    child=$!

    # waits for `tail -f` indefinitely and allows external signals,
    # including docker stop signals, to be captured by `trap`
    wait "$child"

}

if [ -d /logs/ ]
  then
    stopcelery
fi
echo 'test'
