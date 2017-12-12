#!/usr/bin/python3
import json
import datetime
import tornado.log
from tornado import web
import tornado.websocket
# from tornado.concurrent import run_on_executor
import concurrent.futures
from tornado import gen
from tornado.queues import Queue
from tornado.escape import json_encode
from tornado.escape import json_decode
import settings
import database


# executor = concurrent.futures.ThreadPoolExecutor(20)

WS_CLIENTS = set()


def ev_subscribe(subscriber, events):
    for ev in events:
        if ev not in EVENTS.keys():
            EVENTS[ev.upper()] = set()
        EVENTS[ev.upper()].add(subscriber)
        tornado.log.logging.info(f'{subscriber} подписался на {ev.upper()}')


def ev_unsubscribe(subscriber, *args):
    for ev in EVENTS.keys():
        if ev not in ('SUBSCRIBE', 'UNSUBSCRIBE'):
            tornado.log.logging.info(f'ev_unsubscribe {ev}, {EVENTS[ev]}')
            EVENTS[ev.upper()].discard(subscriber)
            tornado.log.logging.info(f'ev_unsubscribe {ev}, {EVENTS[ev]}')


async def ev_propagate(message, self=None):
    tornado.log.logging.info(f'ev_propagate: {message}, {self}')
    ev = tuple(message.keys())[0].upper()
    data = message[ev]
    if ev in ('SUBSCRIBE', 'UNSUBSCRIBE'):
        EVENTS[ev](self, data)
        # tornado.log.logging.info(f'{self} отписался...')
    else:
        if ev in EVENTS.keys():
            for route in EVENTS[ev]:
                if self is not route:
                    try:
                        await route.write_message(json_encode({ev: data}))
                    except Exception as e:
                        tornado.log.logging.critical(e)
    return self


EVENTS = {
    'SUBSCRIBE': ev_subscribe,
    'UNSUBSCRIBE': ev_unsubscribe,
}


class Main(web.RequestHandler):
    async def get(self):
        tornado.log.logging.info('Main')


class InputData(web.RequestHandler):
    async def get(self):
        tornado.log.logging.info('InputData.get')


class Login(web.RequestHandler):
    async def get(self):
        tornado.log.logging.info('Login.get')

    async def post(self):
        tornado.log.logging.info('Login.post')


class Logout(web.RequestHandler):
    async def get(self):
        tornado.log.logging.info('Logout.get')

    async def post(self):
        tornado.log.logging.info('Logout.post')


class SMSMessage(web.RequestHandler):
    async def get(self):
        tornado.log.logging.info(self.request.body)


class VoiceMessage(web.RequestHandler):
    async def get(self):
        tornado.log.logging.info(self.request.body)


class TMABConnect(web.RequestHandler):
    async def get(self, request):
        params = {'startparam1': 'phone0', 'startparam2': 'phone1', }
        self.set_status(200, 'OK')  # Умиротворить ТМСервер
        uri = tornado.escape.url_unescape(self.request.uri)
        tornado.log.logging.info(uri)
        params = {params[r.split('=')[0]] if r.split('=')[0] in params.keys(
        ) else r.split('=')[0]: r.split('=')[1] for r in uri.split('?')[1].split('&')}
        tornado.log.logging.info(params)
        ev_propagate({'CALLBACK_BRIDGE_START': params, })


class SNMP(web.RequestHandler):
    SUPPORTED_METHODS = ('POST',)

    def check_xsrf_cookie(self):
        pass

    def json_serial(self, data):
        if isinstance(data, (datetime.datetime, )):
            return data.__str__()
        return data

    async def post(self):
        self.set_status(200, 'OK')
        tornado.log.logging.info(self.request.body)
        snmp_event = json.loads(self.request.body)
        data = {}
        event = snmp_event['event']
        data[event] = snmp_event
        tornado.log.logging.info(data)
        await ev_propagate(data)


class Devices(web.RequestHandler):
    async def get(self):
        # tornado.log.logging.info(self.request.body)
        devices = await database.load_devices()
        tornado.log.logging.info(devices)
        self.render('devices.html', devices=devices)


class TMHandler(web.RequestHandler):
    async def get(self, request):
        params = {'name': 'event', 'startparam3': 'callback_state',
                  'startparam4': 'order_id', 'startparam1': 'phone',
                  'startparam2': 'phone1'}
        self.set_status(200, 'OK')  # Умиротворить ТМСервер
        # tornado.log.logging.info(self.kwargs)
        # tornado.log.logging.info('TMHandler.name: %s' % self.get_argument('name'))
        uri = tornado.escape.url_unescape(self.request.uri)
        params = {params[r.split('=')[0]] if r.split('=')[0] in params.keys(
        ) else r.split('=')[0]: r.split('=')[1] for r in uri.split('?')[1].split('&')}
        tornado.log.logging.info(params)
        if params['event'] == 'TMABConnect':
            params.update(phones=(params['phone'], params['phone1']))
        else:
            params.update(phone=params['phone'][-10:])
            params.update(request_state=0)
        params.update(event='OKTELL_' + params['event'].upper())
        tornado.log.logging.info(params)
        await ev_propagate({params['event']: params, })


class WSHandler(tornado.websocket.WebSocketHandler):
    async def on_message(self, message):
        tornado.log.logging.info(message)
        message = json_decode(message)
        tornado.log.logging.info(message)
        await ev_propagate(message, self, )

    async def open(self):
        WS_CLIENTS.add(self)
        tornado.log.logging.info(f'{self} connected')

    def on_close(self):
        ev_unsubscribe(self)
        WS_CLIENTS.discard(self)
        tornado.log.logging.info(f'{self} disconnected')

    async def on_error(self):
        tornado.log.logging.error(f'{self} error')
