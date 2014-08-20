# -*- coding: utf-8 -*-
__author__ = 'wangting'
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from web_handlers.page_handler import MainHandler
from web_handlers.socket_handler import WebSocketHandler


application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/ws', WebSocketHandler),
], debug=True)

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9908)
    tornado.ioloop.IOLoop.instance().start()

