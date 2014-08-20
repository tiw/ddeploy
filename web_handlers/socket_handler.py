# -*- coding: utf-8 -*-
import tornado
from tornado.ioloop import PeriodicCallback
from dashboard import Dashboard

__author__ = 'wangting'


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.callback = PeriodicCallback(self.gather_info, 360)
        self.callback.start()

    def gather_info(self):
        d = Dashboard(cgroup_root='/tmp')
        info = d.getInfo(container_id='123')
        self.write_message(info)

    def on_message(self, message):
        pass

    def on_close(self):
        self.callback.stop()
