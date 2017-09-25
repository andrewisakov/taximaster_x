#!/usr/bin/python3
import tornado.ioloop
import tornado.httpserver
from routes import routes_setup
from settings import settings


clients = []


if __name__ == '__main__':
    app = tornado.web.Application(routes_setup(), **settings)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8881)
    tornado.ioloop.IOLoop.current().start()
