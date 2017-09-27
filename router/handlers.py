#!/usr/bin/python3
import tornado.web
import tornado.websocket
from tornado import gen
from tornado.queues import Queue
import tornado.escape


class Login(tornado.web.RedirectHandler):
    @gen.coroutine
    def get(self):
        print('Login.get')

    @gen.coroutine
    def post(self):
        print('Login.post')


class Logout(tornado.web.RedirectHandler):
    @gen.coroutine
    def get(self):
        print('Logout.get')

    @gen.coroutine
    def post(self):
        print('Logout.post')


class TMHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self, request):
        self.set_status(200, 'OK')
        request = tornado.escape.xhtml_unescape(request)
        result = {}
        for r in request.split('&'):
            rr = r.split['=']
            result[rr[0]] = rr[1]
        print(result)

    @gen.coroutine
    def get(self, request):
        self.set_status(200, 'OK')
        print(request)
        result = {}
        for r in request.split('&'):
            print(r)
            rr = r.split('=')
            result[rr[0]] = rr[1]
        print(result)


class WSHandler(tornado.websocket.WebSocketHandler):
    def on_message(self, message):
        print(message)

    def open(self):
        clients.append(self)

    def close(self):
        del clients[self]
