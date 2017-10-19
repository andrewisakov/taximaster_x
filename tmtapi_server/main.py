#!/usr/bin/python3
import os
import tornado.ioloop
import tornado.options
import tornado.httpserver
from routes import routes_setup
import settings


clients = []


if __name__ == '__main__':
    tornado.options.parse_command_line()
    tornado.options.define('log_file_max_size', default=str(10*1024*1024))
    tornado.options.define('log_file_prefix', default='tmtapi_server.log')
    app = tornado.web.Application(routes_setup(), **settings.settings)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port=settings.TMAPI['port'], address=settings.TMAPI['host'])
    tornado.ioloop.IOLoop.current().start()
