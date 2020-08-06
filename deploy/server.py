import subprocess

from flask import Flask, request, Response
import os

app = Flask(__name__)


@app.route('/deploy/')
def deploy():
    key = request.args.get('key', '')
    if not key or key != os.environ['API_KEY']:
        return Response(status=400)

    subprocess.Popen(
        ['/bin/bash', '-c', 'docker pull rttest/project-connect-api:prod && sudo service proco-api restart'],
        stdout=open('deploy.log', 'a'),
        stderr=open('deploy.log', 'a'),
    )
    return 'ok'
