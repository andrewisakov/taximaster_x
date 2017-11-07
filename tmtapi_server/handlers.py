#!/usr/bin/python3
import json
import datetime
import tornado.log
import tornado.web
import dicttoxml
from tornado.httpclient import AsyncHTTPClient
# import tornado.websocket
# from tornado.concurrent import run_on_executor
import concurrent.futures
from tornado import gen
from tornado.queues import Queue
from tornado.escape import json_encode
from tornado.escape import json_decode
import settings
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
    params = {'event': 'name', 'callback_state': 'startparm3' ,
              'order_id': 'startparm4', 'phone': 'startparm1', }

    def check_xsrf_cookie(self):
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

        order = list(filter(lambda x: x['id'] ==
                            data['order_id'], tmtapi.ORDERS))[0]
        order['state'] = data['order_state']
        order['driver_timecount'] = int(data['order_driver_timecount']) if data['order_driver_timecount'] else 0
        data['order_crew_id'] = int(
            data['order_crew_id']) if data['order_crew_id'] else 0
        order['crew_id'] = data['order_crew_id']
        order['state_id'] = tmtapi.ORDER_STATES[data['order_state']][1]
        if order['id'] not in tmtapi.ORDER_H:
            tmtapi.ORDER_H[order['id']] = []
        tmtapi.ORDER_H[data['order_id']].append((datetime.datetime.now(),
                                                 data['order_state'],
                                                 data['order_crew_id'], ))
        if data['order_state'] == 'order_created':
            order['starttime'] = list(filter(
                lambda x: x[1] == 'order_created', tmtapi.ORDER_H[data['order_id']]))[0][0]
        if data['order_state'] == 'order_completed':
            order['finishtime'] = list(filter(
                lambda x: x[1] == 'order_completed', tmtapi.ORDER_H[data['order_id']]))[0][0]
        tornado.log.logging.debug(
            list(filter(lambda x: x['id'] == data['order_id'], tmtapi.ORDERS))[0])
        tornado.log.logging.debug(tmtapi.ORDER_H[data['order_id']])
        response = order
        response.update(code=0)
        self.write(json.dumps(response, default=self.json_serial))
        params = []
        params.append('%s=%s' % (self.params['event'], data['order_state']))
        params.append('%s=%s' % (self.params['callback_state'], 1))
        params.append('%s=%s' % (self.params['order_id'], data['order_id']))
        params.append('%s=%s' % (self.params['phone'], data['order_phone_to_callback']))
        params = '?' + '&'.join(params)
        url = 'http://%s:%s/execsvcscript%s' % (settings.TMAPI['host'], settings.PORT, params)
        http_client = AsyncHTTPClient()
        response = await http_client.fetch(url)
        tornado.log.logging.info(response.request.body)


class get_info_by_order_id(tornado.web.RequestHandler):
    def check_xsrf_cookie(self):
        pass

    async def get(self, request):
        # self.set_status(200, 'OK')
        tornado.log.logging.info(self.request.arguments)
        uri, params = tornado.escape.url_unescape(self.request.uri).split('?')
        params = {p.split('=')[0]: p.split('=')[1] for p in params.split('&')}
        order_id = int(params['order_id'])
        # response = await tmtapi.requests['get_info_by_order_id'](params)
        order = list(filter(lambda x: x['id'] == order_id, tmtapi.ORDERS))[0]
        tornado.log.logging.info(order)
        crew = list(filter(lambda x: x['id'] == order['crew_id'], tmtapi.CREWS))[0]
        car = list(filter(lambda x: x['id'] == crew['car_id'], tmtapi.CARS))[0]
        data = {}
        response = {'response': {'code': 0, 'descr': 'OK', 'data': data}, }
        data.update(car_id=car['id'])
        data.update({k: v for k, v in car.items() if k != 'id'})
        data.update(order_id=order_id)
        data.update({k: v for k, v in order.items() if k != 'id'})
        dicttoxml.set_debug(False)
        response = dicttoxml.dicttoxml(response, root=False, attr_type=False)
        tornado.log.logging.info(response)
        self.write(response)


class get_order_state(tornado.web.RequestHandler):
    async def get(self, request):
        tornado.log.logging.info(request)
        args = self.request.arguments
        args = {k: v[0] for k, v in args.items()}
        order_id = int(args['order_id'])
        tornado.log.logging.info(args)
        order = list(filter(lambda x: x['id'] == order_id, tmtapi.ORDERS))[0]
        crew = list(filter(lambda x: x['id'] == order['crew_id'], tmtapi.CREWS))[0]
        car = list(filter(lambda x: x['id'] == crew['id'], tmtapi.CARS))[0]
        driver = list(filter(lambda x: x['id'] == crew['driver_id'], tmtapi.DRIVERS))[0]
        order_state = {}
        order_state = {
            'order_id': order_id, 'state_id': order['state_id'],
            'crew_id': order['crew_id'],
            'driver_id': driver['id'], 'car_id': car['id'],
            'start_time': order['starttime'],
            'source_time': order['sourcetime'],
            'finish_time': order['finishtime'],
            'source': order['source'], 'destination': order['destination'],
            'phone': order['phone_to_callback'],
            'client_id': order['client_id'],
            'order_crew_group_id': 1,
            'driver_timecount': int(order['driver_timecount']) if order['driver_timecount'] else 0,
            'car_mark': car['mark'], 'car_model': car['model'],
            'car_color': car['color'], 'car_number': car['gosnumber'],
            'confirmed': 'confirmed_by_driver',
            'crew_coords': {'lat': 56.833981, 'lon': 53.220249},
            'order_params': [], 'creation_way': order['creation_way'],
        }
        order_state.update(code=0, descr='OK')
        order_state = json.dumps(order_state, default=self.json_datetime)
        tornado.log.logging.info(order_state)
        self.write(order_state)

    def json_datetime(self, json_parmameter):
        if isinstance(json_parmameter, (datetime.datetime)):
            return json_parmameter.strftime('%Y%m%d%H%M%S')


class set_request_state(tornado.web.RequestHandler):
    def check_xsrf_cookie(self):
        pass

    async def post(self, request):
        params = tornado.escape.url_unescape(self.request.body)
        params = {p.split('=')[0]: p.split('=')[1] for p in params.split('&')}
        tornado.log.logging.info(params)
        order_id = int(params['order_id'])
        callback_state = int(params['state'])
        order = list(filter(lambda x: x['id'] == order_id, tmtapi.ORDERS))[0]
        order['callback_state'] = callback_state
        self.write('<response><code>0</code><descr>OK</descr></response>')


class TM_TAPI(tornado.web.RequestHandler):
    def check_xsrf_cookie(self):
        pass

    async def get(self, request):
        # print('TM_API.get request=', request)

        # self.set_status(200, 'OK')
        uri, params = tornado.escape.url_unescape(self.request.uri).split('?')
        command = uri.split('/')[-1]
        tornado.log.logging.info(f'{command}, {params}')
        params = {r.split('=')[0].upper(): r.split('=')[1]
                  for r in params.split('&')}
        tornado.log.logging.info(params)
        api_result = await tmtapi.requests[command](**params)
        self.write(api_result)

    async def post(self, request):
        # self.set_status(200, 'OK')
        # tornado.log.logging.info(self.kwargs)
        # print(request)
        uri, params = tornado.escape.url_unescape(self.request.uri).split('?')
        command = uri.split('/')[-1]
        tornado.log.logging.info(f'{command}, {params}')
        params = {r.split('=')[0].upper(): r.split('=')[1]
                  for r in params.split('&')}
        tornado.log.logging.info(params)
        api_result = await tmtapi.requests[command](**params)
        self.write(result)


class COMMON_API(tornado.web.RequestHandler):

    async def get(self, request):
        self.set_status(200, 'OK')
        # tornado.log.logging.info(self.kwargs)
        uri = tornado.escape.url_unescape(self.request.uri)
        result = {r.split('=')[0]: r.split('=')[1]
                  for r in uri.split('?')[1].split('&')}
        tornado.log.logging.info(result)

    async def post(self, request):
        self.set_status(200, 'OK')
        # tornado.log.logging.info(self.kwargs)
        uri = tornado.escape.url_unescape(self.request.uri)
        result = {r.split('=')[0]: r.split('=')[1]
                  for r in uri.split('?')[1].split('&')}
        tornado.log.logging.info(result)
