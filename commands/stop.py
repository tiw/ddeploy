# -*- coding: utf-8 -*-
__author__ = 'wangting'

from commands.docker_base import DockerBase
from db import Db


class Stop(DockerBase):
    """

    """

    def stop(self, group_name):
        Db.get_containers(group_name)
        pass

    def stop_and_rm(self):
        pass
