# -*- coding: utf-8 -*-
__author__ = 'wangting'


import tornado.web
import tornado.template


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        import os.path
        _dir = os.path.dirname(os.path.abspath(__file__))
        loader = tornado.template.Loader('%s/../template' % _dir)
        self.write(loader.load('index.html').generate(message="hhhhallllllo wooooorldddddd"))
