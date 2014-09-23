#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'wangting'

from commands.docker_base import DockerBase


class Start(DockerBase):

    def get_volume_mapping(self, name):
        config = self.config.get('base', 'volumes')
        binds = {}
        for volume in config[name]:
            binds[volume[0]] = {'bind': volume[1], 'ro': False}
        return binds

    def build_fpm(self):
        fpm_image = self.d.get_image(self.repo, "php-fpm-gearman")
        fpm_container = self.d.create_container(fpm_image, detach=True, name=self.config.get('base', 'fpm_name'))

        binds = self.get_volume_mapping('fpm')
        # TODO: give the option whether gearman is needed
        self.d.start_container(fpm_container, binds=binds, links={self.config.get('base', 'gearman_name'): "gearman"})
        return fpm_container

    def build_cli(self):
        cli_image = self.d.get_image(self.repo, 'php-cli-pure')
        entry_point = ["/usr/bin/php", "/data/www/oms/service/src/bin/queue.php", "start"]
        cli_container = self.d.create_container(cli_image, detach=True, name=self.config.get('base', 'cli_name'),
                                                entry_point=entry_point)
        binds = self.get_volume_mapping('cli')
        # TODO: give the option whether gearman is needed
        self.d.start_container(cli_container, binds=binds, links={self.config.get('base', 'gearman_name'): "gearman"})
        return cli_container

    def build_cron(self):
        cron_image = self.d.get_image("10.6.1.39:5000/niksun/base-cron", "latest")
        cron_container = self.d.create_container(cron_image, detach=True, name=self.config.get('base', 'cron_name'))
        binds = self.get_volume_mapping('cron')
        self.d.start_container(cron_container, binds=binds, links={self.config.get('base', 'gearman_name'): "gearman"})
        return cron_container

    def build_gearman(self):
        gearman_image = self.d.get_image(self.repo, 'gearman')
        gearman_container = self.d.create_container(
            gearman_image,
            detach=True,
            name=self.config.get('base', 'gearman_name')
        )
        self.d.start_container(gearman_container)
        return gearman_container

    def build_nginx(self):
        binds = self.get_volume_mapping('nginx')
        nginx_image = self.d.get_image(self.repo, "nginx")
        nginx_container = self.d.create_container(
            nginx_image, detach=True, name=self.config.get('base', 'nginx_name')
        )
        self.d.start_container(
            nginx_container, binds=binds,
            publish_all_ports=True,
            links={self.config.get('base', 'fpm_name'): "fpm"},
            port_bindings={80: self.config.get('base', 'local_nginx_port')}
        )
        return nginx_container
