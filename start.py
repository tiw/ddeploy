#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'wangting'

import sqlite3 as lite
from utils import DockerUtils


class Start:
    def __init__(self, config):
        self.config = config
        self.repo = config.get('base', 'DOCKER_HOST') + '/ting/ubuntu'
        self.d = DockerUtils(config.get('base', 'DOCKER_BASE_URL'))

    def getVolumeMapping(self, name):
        config = self.config['volumes']
        binds = {}
        for volume in config[name]:
            binds[volume[0]] = {'bind': volume[1], 'ro': False}
        return binds

    def buildFpm(self):
        fpm_image = self.d.getImage(self.repo, "php-fpm-gearman")
        fpm_container = self.d.createContainer(fpm_image, detach=True, name=self.config['fpm_name'])

        binds = self.getVolumeMapping('fpm')
        # TODO: give the option whether gearman is needed
        self.d.startContainer(fpm_container, binds=binds, links={self.config['gearman_name']: "gearman"})
        return fpm_container

    def buildCli(self):
        cli_image = self.d.getImage(self.repo, 'php-cli-pure')
        entry_point = ["/usr/bin/php", "/data/www/oms/service/src/bin/queue.php", "start"]
        cli_container = self.d.createContainer(cli_image, detach=True, name=self.config['cli_name'], entry_point=entry_point)
        binds = self.getVolumeMapping('cli')
        # TODO: give the option whether gearman is needed
        self.d.startContainer(cli_container, binds=binds, links={self.config['gearman_name']: "gearman"})
        return cli_container

    def buildGearman(self):
        gearman_image = self.d.getImage(self.repo, 'gearman')
        gearman_container = self.d.createContainer(
            gearman_image,
            detach=True,
            name=self.config.get('base', 'gearman_name')
        )
        r = self.d.startContainer(gearman_container)
        return gearman_container

    def buildNginx(self):
        binds = self.getVolumeMapping('nginx')
        nginx_image = self.d.getImage(self.repo, "nginx")
        nginx_container = self.d.createContainer(
            nginx_image, detach=True, name=self.config['nginx_name']
        )
        r = self.d.startContainer(nginx_container, binds=binds,
                             publish_all_ports=True,
                             links={self.config['fpm_name']: "fpm"},
                             port_bindings={80: self.config['local_nginx_port']}
        )
        return nginx_container


