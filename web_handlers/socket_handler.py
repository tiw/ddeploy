# -*- coding: utf-8 -*-
import tornado
from tornado.ioloop import PeriodicCallback
from dashboard import Dashboard
import json

__author__ = 'wangting'


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.callback = PeriodicCallback(self.gather_info, 360)
        self.callback.start()

    def gather_info(self):
        d = Dashboard(cgroup_root='/tmp')
        raw_info = d.getInfo(container_id='123')
        l = raw_info.split("\n")
        info = dict()
        for p in l:
            i = p.split(" ")
            if len(i) == 2:
                info[i[0]] = i[1]
        self.write_message(json.dumps(info))

    def on_message(self, message):
        pass

    def on_close(self):
        self.callback.stop()
