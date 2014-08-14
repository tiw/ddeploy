# -*- coding: utf-8 -*-
__author__ = 'wangting'

import sqlite3 as lite


def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_instance


@singleton
class Db:
    def __init__(self, db_file):
        self.db_file = db_file
        self.con = lite.connect(self.db_file)

    def __save_sys_info(self, sys_name, idh, name):
        idh = idh[u'Id']
        cur = self.con.cursor()
        cur.execute("INSERT INTO system_infos VALUES(?, ?, ?)", (sys_name, idh, name))
        self.con.commit()

    def persist_system(self, sys_name, containers):
        for container in containers:
            (idh, name) = container
            self.__save_sys_info(sys_name, idh, name)

    def search_container(self):
        self.con.row_factory = lite.Row
        cur = self.con.cursor()
        cur.execute("SELECT * FROM system_infos")
        return cur.fetchall()

    def get_containers(self, group_name):
        self.con.row_factory = lite.Row
        cur = self.con.cursor()
        cur.execute("SELECT ContainerId FROM system_infos WHERE SystemName = ?", group_name)
        return cur.fetchall()

