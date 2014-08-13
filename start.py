#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'wangting'

from pprint import pprint
import docker
import sqlite3 as lite
import json


def parser_config(conf):
    json_data = open(conf)
    return json.load(json_data)

conf = parser_config('./config.json')
DOCKER_HOST = conf['DOCKER_HOST']
DOCKER_BASE_URL = conf['DOCKER_BASE_URL']
DATA_DIR = '/data'
DB_FILE = conf['DB_FILE']


class DockerUtils:
    def __init__(self):
        self.c = docker.Client(
            base_url=DOCKER_BASE_URL,
            version="1.12", timeout=50)

    def getImage(self, name, tag):
        repositories = self.c.images(name)
        repo_name = u'%s:%s' % (name, tag)
        images = [i for i in repositories if repo_name in i[u'RepoTags']]
        if len(images) != 1:
            raise Exception("None or more than one image are found")
        return images[0]

    def createContainer(self, image, detach=False, name=None, command=None, entry_point=None):
        pprint(image)
        image_id = image['Id']
        return self.c.create_container(image_id, detach=detach, name=name, command=command, entrypoint=entry_point)

    def startContainer(self, container, binds=None, links=None, publish_all_ports=None, port_bindings=None):
        return self.c.start(container, binds=binds, links=links, publish_all_ports=publish_all_ports,
                            port_bindings=port_bindings)

    def stopContainer(self, container):
        self.c.stop(container)

    def removeContainer(self, container):
        self.c.remove_container(container)


# input
local_nginx_port = 8813
root_dir = 'oms_staging'
nginx_config_dir = ''


fpm_name = root_dir.replace('_', '-') + u'-fpm'
nginx_name = root_dir.replace('_', '-') + u'-nginx'
gearman_name = root_dir.replace('_', '-') + u'-gearman'
cli_name = root_dir.replace('_', '-') + u'-cli'
log_dir = DATA_DIR + '/logs/' + root_dir
src_dir = DATA_DIR + '/src/' + root_dir

config = {
    'fpm': [
        (src_dir, '/data/www/oms'),
        (log_dir, '/data/logs/oms')
    ],
    'nginx': [
        (src_dir, '/data/www/oms'),
        (src_dir + '/' + nginx_config_dir, '/etc/nginx/sites-enabled'),
        (log_dir, '/data/logs/oms')
    ],
    'cli': [
        (src_dir + root_dir, '/data/www/oms')
    ]
}


def getVolumeMapping(name):
    binds = {}
    for volume in config[name]:
        binds[volume[0]] = {'bind': volume[1], 'ro': False}
    return binds


def buildFpm(name):
    d = DockerUtils()
    ting_repo = DOCKER_HOST + "/ting/ubuntu"

    fpm_image = d.getImage(ting_repo, "php-fpm-gearman")
    fpm_container = d.createContainer(fpm_image, detach=True, name=name)

    binds = getVolumeMapping('fpm')
    # TODO: give the option whether gearman is needed
    d.startContainer(fpm_container, binds=binds, links={gearman_name: "gearman"})
    return fpm_container


def buildCli(name):
    d = DockerUtils()
    ting_repo = DOCKER_HOST + "/ting/ubuntu"

    cli_image = d.getImage(ting_repo, 'php-cli-pure')
    entry_point = ["/usr/bin/php", "/data/www/oms/service/src/bin/queue.php", "start"]
    cli_container = d.createContainer(cli_image, detach=True, name=name, entry_point=entry_point)
    binds = getVolumeMapping('cli')
    # TODO: give the option whether gearman is needed
    d.startContainer(cli_container, binds=binds, links={gearman_name: "gearman"})
    return cli_container


def buildGearman(name):
    d = DockerUtils()
    ting_repo = DOCKER_HOST + "/ting/ubuntu"
    gearman_image = d.getImage(ting_repo, 'gearman5')
    gearman_container = d.createContainer(gearman_image, detach=True, name=name)
    r = d.startContainer(gearman_container)
    return gearman_container


def buildNginx(name):
    d = DockerUtils()
    ting_repo = DOCKER_HOST + "/ting/ubuntu"

    binds = getVolumeMapping('nginx')
    nginx_image = d.getImage(ting_repo, "nginx")
    nginx_container = d.createContainer(
        nginx_image, detach=True, name=name
    )
    r = d.startContainer(nginx_container, binds=binds,
                         publish_all_ports=True,
                         links={fpm_name: "fpm"},
                         port_bindings={80: local_nginx_port}
    )
    return nginx_container


con = lite.connect(DB_FILE)


def save_sys_info(sys_name, id, name):
    con.execute("INSERT INTO system_infos VALUES(?, ?, ?)", (sys_name, id, name))


def persistSystem(sys_name, containers):
    for container in containers:
        (id, name) = container
        save_sys_info(sys_name, id, name)

if __name__ == "__main__":
    d = DockerUtils()
    containers = []
    try:
        gearman_container_id = buildGearman(gearman_name)
        # fpm_container_id = buildFpm(fpm_name)
        # nginx_container_id = buildNginx(nginx_name)
        # cli_container_id = buildCli(cli_name)
        containers.append(gearman_container_id)
        # containers.append(fpm_container_id)
        # containers.append(nginx_container_id)
        # containers.append(cli_name)
        persistSystem(root_dir, [
            (gearman_container_id, gearman_name)
            # (fpm_container_id, fpm_name),
            # (nginx_container_id, nginx_name),
            # (cli_container_id, cli_name)
            ])
    except Exception as e:
        for container in containers:
            d.stopContainer(container)
            d.removeContainer(container)
            pprint(e)
