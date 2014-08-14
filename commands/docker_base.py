# -*- coding: utf-8 -*-
__author__ = 'wangting'

from utils import DockerUtils


class DockerBase:
    def __init__(self, config):
        self.config = config
        self.repo = config.get('base', 'DOCKER_HOST') + '/ting/ubuntu'
        self.d = DockerUtils(config.get('base', 'DOCKER_BASE_URL'))
