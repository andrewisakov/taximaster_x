#!/usr/bin/python3
import json
import datetime
import tornado.log
import tornado.web
# import tornado.websocket
# from tornado.concurrent import run_on_executor
import concurrent.futures
from tornado import gen
from tornado.queues import Queue
from tornado.escape import json_encode
from tornado.escape import json_decode
import tmtapi


# executor = concurrent.futures.ThreadPoolExecutor(20)

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
        self.render('orders.html',
                    orders=tmtapi.ORDERS,
                    order_states=tmtapi.ORDER_STATES,
                    order_h=tmtapi.ORDER_H,
                    drivers=tmtapi.DRIVERS,
                    cars=tmtapi.CARS,
                    crews=tmtapi.CREWS)


class ChangeOrderState(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ('POST',)
    async def check_xsrf_cookie(self):
        pass

    def json_serial(self, data):
        if isinstance(data, (datetime.datetime, )):
            return data.__str__()
        return data

    async def post(self):
        tornado.log.logging.info(self.request.body)
        data = json.loads(self.request.body)
        data['order_id'] = int(data['order_id'])
        tornado.log.logging.debug(data)

        order = list(filter(lambda x: x['id'] == data['order_id'], tmtapi.ORDERS))[0]
        order['state'] = data['order_state']
        data['order_crew_id'] = int(data['order_crew_id']) if data['order_crew_id'] else 0
        if order['id'] not in tmtapi.ORDER_H:
            tmtapi.ORDER_H[order['id']] = []
        tmtapi.ORDER_H[data['order_id']].append((datetime.datetime.now(),
                                                 data['order_state'],
                                                 data['order_crew_id'], ))
        if data['order_state'] == 'order_created':
            order['starttime'] = list(filter(lambda x: x[1] == 'order_created', tmtapi.ORDER_H[data['order_id']]))[0][0]
        if data['order_state'] == 'order_completed':
            order['finishtime'] = list(filter(lambda x: x[1] == 'order_completed', tmtapi.ORDER_H[data['order_id']]))[0][0]
        tornado.log.logging.debug(list(filter(lambda x: x['id'] == data['order_id'], tmtapi.ORDERS))[0])
        tornado.log.logging.debug(tmtapi.ORDER_H[data['order_id']])
        response = order
        response.update(code=0)
        self.write(json.dumps(response, default=self.json_serial))


class TM_TAPI(tornado.web.RequestHandler):

    # @gen.coroutine
    async def get(self, request):
        print('TM_API.get request=', request)

        # self.set_status(200, 'OK')
        uri, params = tornado.escape.url_unescape(self.request.uri).split('?')
        command = uri.split('/')[-1]
        tornado.log.logging.info(f'{command}, {params}')
        params = {r.split('=')[0].upper(): r.split('=')[1] for r in params.split('&')}
        tornado.log.logging.info(params)
        api_result = await tmtapi.requests[command](**params)
        self.write(api_result)

    async def post(self, request):
        # self.set_status(200, 'OK')
        # tornado.log.logging.info(self.kwargs)
        print(request)
        uri, params = tornado.escape.url_unescape(self.request.uri).split('?')
        command = uri.split('/')[-1]
        tornado.log.logging.info(f'{command}, {params}')
        params = {r.split('=')[0].upper(): r.split('=')[1] for r in params.split('&')}
        tornado.log.logging.info(params)
        api_result = await tmtapi.requests[command](**params)
        self.write(result)


class COMMON_API(tornado.web.RequestHandler):

    async def get(self, request):
        self.set_status(200, 'OK')
        # tornado.log.logging.info(self.kwargs)
        uri = tornado.escape.url_unescape(self.request.uri)
        result = {r.split('=')[0]: r.split('=')[1] for r in uri.split('?')[1].split('&')}
        tornado.log.logging.info(result)

    async def post(self, request):
        self.set_status(200, 'OK')
        # tornado.log.logging.info(self.kwargs)
        uri = tornado.escape.url_unescape(self.request.uri)
        result = {r.split('=')[0]: r.split('=')[1] for r in uri.split('?')[1].split('&')}
        tornado.log.logging.info(result)
