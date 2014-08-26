# -*- coding: utf-8 -*-
from pprint import pprint

__author__ = 'wangting'
from flask import Flask, jsonify, Response
from flask_script import Manager, Shell
from utils import DockerUtils, parser_config

app = Flask(__name__)
app.debug = True
import os.path
_dir = os.path.dirname(os.path.abspath(__file__))
config = parser_config(os.path.join(_dir, 'config.json'))

manager = Manager(app=app)

@app.route('/containers')
def list_containers():
    d = DockerUtils(base_url=config['DOCKER_BASE_URL'])
    containers = d.get_containers()
    pprint(containers)
    return jsonify({"containers": containers})


@app.route('/container/start/<container_id>')
def start_container(container_id):
    d = DockerUtils(base_url=config['DOCKER_BASE_URL'])
    try:
        d.start_container({'Id': container_id})
    except Exception as e:
        return Response(status=500)
    return Response(status=200)




manager.run()