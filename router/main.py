#!/usr/bin/python3
import tornado.ioloop
import tornado.options
import tornado.httpserver
from routes import routes_setup
import settings


clients = []


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(routes_setup(), **settings.settings)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(settings.PORT)
    tornado.ioloop.IOLoop.current().start()
