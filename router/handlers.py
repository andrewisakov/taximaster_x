#!/usr/bin/python3
import json
import tornado.log
import tornado.web
import tornado.websocket
# from tornado.concurrent import run_on_executor
import concurrent.futures
from tornado import gen
from tornado.queues import Queue
from tornado.escape import json_encode
from tornado.escape import json_decode


executor = concurrent.futures.ThreadPoolExecutor(20)

WS_CLIENTS = set()


def ev_subscribe(subscriber, events):
    for ev in events:
        if ev not in EVENTS.keys():
            EVENTS[ev] = set()
        EVENTS[ev.upper()].add(subscriber)
        tornado.log.logging.info(f'{subscriber} подписался на {ev.upper()}')


def ev_unsubscribe(subscriber, *args):
    for ev in EVENTS.keys():
        if ev not in ('SUBSCRIBE', 'UNSUBSCRIBE'):
            tornado.log.logging.info(f'ev_unsubscribe {ev}, {EVENTS[ev]}')
            EVENTS[ev].discard(subscriber)
            tornado.log.logging.info(f'ev_unsubscribe {ev}, {EVENTS[ev]}')


async def ev_propagate(self, message):
    tornado.log.logging.info(f'ev_propagate: {message}, {self}')
    ev = tuple(message.keys())[0].upper()
    data = message[ev]
    if ev in ('SUBSCRIBE', 'UNSUBSCRIBE'):
        EVENTS[ev](self, data)
        tornado.log.logging.info(f'{self} отписался...')
    else:
        for route in EVENTS[ev]:
            try:
                if self is not route:
                    await route.send_message(json_encode({ev: data}))
            except Exception as e:
                tornado.log.logging.critical(e)

    return self


EVENTS = {
    'SUBSCRIBE': ev_subscribe,
    'UNSUBSCRIBE': ev_unsubscribe,
         }


class Main(tornado.web.RequestHandler):
    async def get(self):
        tornado.log.logging.info('Main')


class InputData(tornado.web.RequestHandler):
    async def get(self):
        tornado.log.logging.info('InputData.get')


class Login(tornado.web.RequestHandler):
    async def get(self):
        tornado.log.logging.info('Login.get')

    async def post(self):
        tornado.log.logging.info('Login.post')


class Logout(tornado.web.RequestHandler):
    async def get(self):
        tornado.log.logging.info('Logout.get')

    async def post(self):
        tornado.log.logging.info('Logout.post')


class TMHandler(tornado.web.RequestHandler):
    # @gen.coroutine
    async def post(self, request):
        self.set_status(200, 'OK')
        request = tornado.escape.xhtml_unescape(request)
        result = {}
        for r in request.split('&'):
            rr = r.split['=']
            result[rr[0]] = rr[1]
        tornado.log.logging.info(result)

    async def get(self, request):
        self.set_status(200, 'OK')
        tornado.log.logging.info(request)
        result = {}
        for r in request.split('&'):
            rr = r.split('=')
            result[rr[0]] = rr[1]
        tornado.log.logging.info(result)


class WSHandler(tornado.websocket.WebSocketHandler):
    async def on_message(self, message):
        tornado.log.logging.info(message)
        message = json_decode(message)
        await ev_propagate(self, message)

    async def open(self):
        WS_CLIENTS.add(self)
        tornado.log.logging.info(f'{self} connected')

    def on_close(self):
        ev_unsubscribe(self)
        WS_CLIENTS.discard(self)
        tornado.log.logging.info(f'{self} disconnected')

    async def on_error(self):
        tornado.log.logging.error(f'{self} error')
