# -*- coding: utf-8 -*-
__author__ = 'wangting'

import json, docker


def parser_config(conf):
    json_data = open(conf)
    return json.load(json_data)


class DockerUtils:
    def __init__(self, base_url):
        self.c = docker.Client(
            base_url=base_url,
            version="1.12", timeout=50)

    def getImage(self, name, tag):
        repositories = self.c.images(name)
        repo_name = u'%s:%s' % (name, tag)
        images = [i for i in repositories if repo_name in i[u'RepoTags']]
        if len(images) != 1:
            raise Exception("%s, None or more than one image are found" % repo_name)
        return images[0]

    def createContainer(self, image, detach=False, name=None, command=None, entry_point=None):
        image_id = image['Id']
        return self.c.create_container(image_id, detach=detach, name=name, command=command, entrypoint=entry_point)

    def startContainer(self, container, binds=None, links=None, publish_all_ports=None, port_bindings=None):
        return self.c.start(container, binds=binds, links=links, publish_all_ports=publish_all_ports,
                            port_bindings=port_bindings)

    def stopContainer(self, container):
        self.c.stop(container)

    def removeContainer(self, container):
        self.c.remove_container(container)
