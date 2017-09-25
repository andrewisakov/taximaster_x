#!/usr/bin/python3
import tornado.web
import tornado.websocket
from tornado import gen
from tornado.queues import Queue


class TMHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self, ):
        self.set_status(200, 'OK')


class WSHandler(tornado.websocket.WebSocketHandler):
    def on_message(self, message):
        print(message)

    def open(self):
        clients.append(self)

    def close(self):
        del clients[self]
