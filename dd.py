#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'wangting'

from pprint import pprint
import os.path

from cement.core import foundation, controller

from commands.start import Start
from commands.list import List
from commands.stop import Stop
from commands.monitor import Monitor
from utils import DockerUtils, parser_config
from db import Db
_dir = os.path.dirname(os.path.abspath(__file__))
conf = parser_config('%s/config.json' % _dir)
conf['DATA_DIR'] = '/data'


# input
conf["local_nginx_port"] = 8813
conf["root_dir"] = 'pdm_staging'
conf['DB_FILE'] = './test.db'
conf['app_name'] = 'pdm'


root_dir = conf['root_dir']
conf['fpm_name'] = root_dir.replace('_', '-') + u'-fpm'
conf['nginx_name'] = root_dir.replace('_', '-') + u'-nginx'
conf['gearman_name'] = root_dir.replace('_', '-') + u'-gearman'
conf['cli_name'] = root_dir.replace('_', '-') + u'-cli'
conf['cron_name'] = root_dir.replace('_', '-') + u'-cron'
log_dir = conf['DATA_DIR'] + '/logs/' + root_dir
src_dir = conf['DATA_DIR'] + '/src/' + root_dir

conf["nginx_config_dir"] = '/deployment/config/nginx/sites_enabled'

conf['volumes'] = {
    'fpm': [
        (src_dir, '/data/www/' + conf["app_name"]),
        (log_dir, '/data/logs/' + conf["app_name"]),
        (conf['DATA_DIR'] + '/images' + '/' + root_dir, '/data/images/pdm/')
    ],
    'nginx': [
        (src_dir, '/data/www/' + conf["app_name"]),
        (src_dir + '/' + conf['nginx_config_dir'], '/etc/nginx/sites-enabled'),
        (log_dir, '/data/logs/' + conf["app_name"]),
        (conf['DATA_DIR'] + '/images' + '/' + root_dir, '/data/images/pdm/')
    ],
    'cli': [
        (src_dir + root_dir, '/data/www/' + conf["app_name"])
    ],
    'cron': [
        (src_dir, '/data/src'),
        (log_dir, '/data/logs'),
        (conf['DATA_DIR'] + '/etc/crontab', '/data/etc/crontab')
    ]
}


class BaseController(controller.CementBaseController):
    class Meta:
        label = 'base'
        description = 'List containers'
        arguments = [
            (['-g', '--group_name'], dict(action="store")),
            (['-c', '--container_id'], dict(action="store")),
            (['-l', '--container_ids'], dict(action="store")),
            (['-v', '--verbose'], dict(action="store_true"))
        ]

    @controller.expose(help='List container group')
    def list(self):
        l = List(self.app.config)
        cs = l.list_all()
        for sys_name in cs.keys():
            print(sys_name)
            for d in cs[sys_name]:
                print "\t\t %s \t %s \t%s" % d

    @controller.expose(help='Stop container group')
    def stop(self):
        group_name = self.app.pargs.group_name
        sc = Stop(self.app.config)
        sc.stop(group_name=group_name)

    @controller.expose(help='Monitoring the container')
    def monitor(self):
        m = Monitor(self.app.config)
        emails = self.app.config.get('base', 'WATCH_EMAILS')
        if None != self.app.pargs.container_id:
            container_id = self.app.pargs.container_id
            m.monitor_container(container_id, emails)
        elif None != self.app.pargs.container_ids:
            container_ids = self.app.pargs.container_ids.split(',')
            container_ids = [container_id.strip() for container_id in container_ids]
            m.monitor_containers(container_ids, emails)


    @controller.expose(help='Remove containers in the group')
    def rm(self):
        group_name = self.app.pargs.group_name
        sc = Stop(self.app.config)
        sc.rm(group_name)

    @controller.expose(help="Stop and remove container in the group")
    def sr(self):
        group_name = self.app.pargs.group_name
        sc = Stop(self.app.config)
        sc.stop_and_rm(group_name)


    @controller.expose(help='Start a group of containers')
    def start(self):
        group_name = self.app.pargs.group_name
        start_list = ['gearman', 'fpm', 'nginx', 'cron']
        db = Db(self.app.config.get('base', 'DB_FILE'))
        containers = []
        start = Start(self.app.config)
        d = DockerUtils(self.app.config.get('base', 'DOCKER_BASE_URL'))
        try:
            for app_name in start_list:
                if app_name == 'gearman':
                    gearman_container_id = start.build_gearman()
                    containers.append(gearman_container_id)
                    db.persist_system(group_name, [(gearman_container_id, self.app.config.get('base', 'gearman_name'))])
                elif app_name == 'fpm':
                    fpm_container_id = start.build_fpm()
                    containers.append(fpm_container_id)
                    db.persist_system(group_name, [(fpm_container_id, self.app.config.get('base', 'fpm_name'))])
                elif app_name == 'nginx':
                    nginx_container_id = start.build_nginx()
                    containers.append(nginx_container_id)
                    db.persist_system(group_name, [(nginx_container_id, self.app.config.get('base', 'nginx_name'))])
                elif app_name == 'cli':
                    cli_container_id = start.build_cli()
                    containers.append(cli_container_id)
                    db.persist_system(group_name, [(cli_container_id, self.app.config.get('base', 'cli_name'))])
                elif app_name == 'cron':
                    cron_container_id = start.build_cron()
                    containers.append(cron_container_id)
                    db.persist_system(group_name, [(cron_container_id, self.app.config.get('base', 'cron_name'))])
        except Exception as e:
            for container in containers:
                d.stop_container(container)
                d.remove_container(container)
            pprint(["error", e])


class DdApp(foundation.CementApp):
    class Meta:
        label = 'Manage_Docker_in_group'
        base_controller = BaseController

app = DdApp(config_defaults={'base': conf})
try:
    app.setup()
    app.run()
finally:
    app.close()
