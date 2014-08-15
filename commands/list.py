# -*- coding: utf-8 -*-
__author__ = 'wangting'

from commands.docker_base import DockerBase
from db import Db
from utils import DockerUtils


class List(DockerBase):
    """
    For listing containers
    """

    def __init__(self, config):
        DockerBase.__init__(self, config)
        self.db = Db(self.config.get('base', 'DB_FILE'))
        self.docker_utils = DockerUtils(config.get('base', 'DOCKER_BASE_URL'))

    def list_all(self):
        # get all container id from DB
        containers = self.db.search_container()
        unified_list = {}
        for container in containers:
            if not (container['SystemName'] in unified_list):
                unified_list[container['SystemName']] = []

            details = self.docker_utils.get_container_details(container['ContainerId'])
            ip = details[u'NetworkSettings'][u'IPAddress']
            unified_list[container['SystemName']].append(
                (container['ContainerName'], container['ContainerId'][:4], ip)
            )

        return unified_list
        pass

    def list_group(self, group_name):
        pass
