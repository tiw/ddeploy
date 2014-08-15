# -*- coding: utf-8 -*-
from pprint import pprint

__author__ = 'wangting'

from commands.docker_base import DockerBase
from db import Db


class Stop(DockerBase):
    """

    """

    def __init__(self, config):
        DockerBase.__init__(self, config)
        self.db = Db(self.config.get('base', 'DB_FILE'))

    def stop(self, group_name):
        rows = self.db.get_containers(group_name)
        for row in rows:
            container_id = row['ContainerId']
            self.d.stop_container({'Id': container_id})

    def rm(self, group_name):
        rows = self.db.get_containers(group_name)
        for row in rows:
            container_id = row['ContainerId']
            self.d.remove_container({'Id': container_id})

    def stop_and_rm(self, group_name):
        self.stop(group_name)
        self.rm(group_name)
        pass
