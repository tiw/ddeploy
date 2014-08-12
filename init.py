# -*- coding: utf-8 -*-
__author__ = 'wangting'
import sqlite3 as lite


con = lite.connect('./test.db')
con.execute("CREATE TABLE system_infos(SystemName TEXT, ContainerId TEXT, ContainerName TEXT)")
