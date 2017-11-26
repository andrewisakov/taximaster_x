#!/usr/bin/python3
import os
# import logging
import aiohttp
import asyncio
# import psycopg2 as pg2
# import aiopg
# import asyncpg
# import fdb
import orders.settings as settings
# import websocket_cli as wscli
from orders.settings import logger
import orders.database as db


orders = {}
cars = {}


def event_result(future):
    """Событие обработано, дальнейшие действия"""
    event, events, order_data = future.result()
    print(f'event_result: {event}, {events}, {order_data}')

    if event in ('ORDER_COMPLETED', 'ORDER_ABORTED'):
        del orders[order_data['order_id']]
    logger.info(f'{event}, {events}, {order_data}')


@asyncio.coroutine
def gen_sms(order_data):
    mark = order_data['mark']
    model = order_data['model']
    color = order_data['color']
    gosnumber = order_data['gosnumber']
    driver_timecount = order_data['drivertimecount']
    yield (f'{mark} {model}\n{color}\n{gosnumber}\n{driver_timecount}'
           '\nРасчёт по таксометру')


@asyncio.coroutine
def gen_message(order_data):
    return ''


@asyncio.coroutine
def created(event, order_data, ws, loop):
    """Фиксация события 'ORDER_CREATED'"""
    events = []  # Никакого события попрождать не надо
    with (yield from orders[order_data['order_id']]['semaphore']):
        orders[order_data['order_id']]['events'].append(order_data)
    return event, events, order_data  # , orders[order_data['order_id']]['events'][:]


@asyncio.coroutine
def completed(event, order_data, ws, loop):
    """Заказ выполнен. Удалить executor для заказа id"""
    events = []
    with (yield from orders[order_data['order_id']]['semaphore']):
        orders[order_data['order_id']]['events'].append(order_data)
    return event, events, order_data  # , orders[order_data['order_id']]['events']


@asyncio.coroutine
def aborted(event, order_data, ws, loop):
    """Заказ прекращён. Удалить executor для заказа id"""
    events = []
    with (yield from orders[order_data['order_id']]['semaphore']):
        orders[order_data['order_id']]['events'].append(order_data)
        # print('aborted:', event, order_data)
    return event, events, order_data  # , orders[order_data['order_id']]['events']


@asyncio.coroutine
def client_gone(event, order_data, ws, loop):
    """Клиент не выходит"""
    events = []
    # order_data['phones'] = normailze_phones(order_data['phones'])
    if order_data['phones']:
        with (yield from orders[order_data['order_id']]['semaphore']):
            orders[order_data['order_id']]['events'].append(order_data)
            events = ['CALLBACK_START', ]
            yield from ws.send_json({'CALLBACK_START': order_data, })
            # print('client_gone:', event, order_data)
    return event, events, order_data  # , orders[order_data['order_id']]['events']


@asyncio.coroutine
def accepted(event, order_data, ws, loop):
    """Заказ принят водителем"""
    events = []
    # order_data['phones'] = normailze_phones(order_data['phones'])
    if order_data['phones']:
        with (yield from orders[order_data['order_id']]['semaphore']):
            orders[order_data['order_id']]['events'].append(order_data)
            events = ['CALLBACK_START', 'SMS_SEND']
            yield from ws.send_json({'CALLBACK_START': order_data, })
            yield from ws.send_json({'SMS_SEND': order_data, })
            # print('accepted:', event, order_data)
    return event, events, order_data  # , orders[order_data['order_id']]['events']


@asyncio.coroutine
def client_fuck(event, order_data, ws, loop):
    """Клиент не вышел. Удалить executor для заказа id"""
    events = []
    # order_data['phones'] = normailze_phones(order_data['phones'])
    if order_data['phones']:
        with (yield from orders[order_data['order_id']]['semaphore']):
            orders[order_data['order_id']]['events'].append(order_data)
            # events = []
            # print('client_fuck:', event, order_data)
    return event, events, order_data  # , orders[order_data['order_id']]['events']


@asyncio.coroutine
def callback_delivered(event, order_data, ws, loop):
    """Отзвон выполнен"""
    events = []
    with (yield from orders[order_data['order_id']]['semaphore']):
        orders[order_data['order_id']]['events'].append(order_data)
        # events = []
        # print('callback_delivered:', event, order_data)
    return event, events, order_data  # , orders[order_data['order_id']]['events']


@asyncio.coroutine
def callback_error(event, order_data, ws, loop):
    """Ошибка отзвона"""
    events = []
    with (yield from orders[order_data['order_id']]['semaphore']):
        last_event = orders[order_data['order_id']]['events'][-1]['event']
        orders[order_data['order_id']]['events'].append(order_data)
        if last_event not in EVENTS[order_data['order_id']][1:]:
            events = ['CALLBACK_START', ]
            yield from ws.send_json({'CALLBACK_START': order_data, })
        else:
            # logger.info(f'last event {last_event} is blocing {event}')
            logger.debug(f'last event {last_event} is blocing {event}')
            # events = []
    return event, events, order_data  # , orders[order_data['order_id']]['events']


@asyncio.coroutine
def callback_busy(event, order_data, ws, loop):
    """Занято"""
    events = []
    with (yield from orders[order_data['order_id']]['semaphore']):
        last_event = orders[order_data['order_id']]['events'][-1]['event']
        orders[order_data['order_id']]['events'].append(order_data)
        if event not in EVENTS[order_data['id']][1:]:
            events = ['CALLBACK_START', ]
            yield from ws.send_json({'CALLBACK_START': order_data, })
        else:
            # logger.info(f'last event {last_event} is blocing {event}')
            logger.debug(f'last event {last_event} is blocing {event}')
            # events = []
    return event, events, order_data  # , orders[order_data['order_id']]['events']


@asyncio.coroutine
def callback_started(event, order_data, ws, loop):
    """Отзвон начат"""
    events = []
    with (yield from orders[order_data['order_id']]['semaphore']):
        orders[order_data['order_id']]['events'].append(order_data)
        # events = []
        # print('callback_started:', event, order_data)
    return event, events, order_data  # , orders[order_data['order_id']]['events']


@asyncio.coroutine
def callback_temporary_error(event, order_data, ws, loop):
    """Времнная ошибка отзвона. Повторить"""
    events = []
    with (yield from orders[order_data['order_id']]['semaphore']):
        last_event = orders[order_data['order_id']]['events'][-1]['event']
        orders[order_data['order_id']]['events'].append(order_data)
        if event not in EVENTS[order_data['order_id']][1:]:
            events = ['CALLBACK_START', ]
            yield from ws.send_json({'CALLBACK_START': order_data, })
        else:
            # print(f'last event {last_event} is blocing {event}')
            logger.debug(f'last event {last_event} is blocing {event}')
            # events = []
    return event, events, order_data  # , orders[order_data['order_id']]['events']


@asyncio.coroutine
def sms_sended(event, order_data, ws, loop):
    """СМС отправлена"""
    events = []
    with (yield from orders[order_data['order_id']]['semaphore']):
        orders[order_data['order_id']]['events'].append(order_data)
        events = []
        # print('sms_sended:', event, order_data)
    return event, events, order_data  # , orders[order_data['order_id']]['events']


@asyncio.coroutine
def sms_error(event, order_data, ws, loop):
    """Ошибка отправки СМС"""
    events = []
    with (yield from orders[order_data['order_id']]['semaphore']):
        orders[order_data['order_id']]['events'].append(order_data)
        # events = []
        # print('sms_error:', event, order_data)
    return event, events, order_data  # , orders[order_data['order_id']]['events']


EVENTS = {
    'ORDER_CREATED': (created, ),
    # 'ORDER_CREATE': create,
    'ORDER_ACCEPTED': (accepted, ),
    'ORDER_COMPLETED': (completed, ),
    'ORDER_ABORTED': (aborted, ),
    'ORDER_CLIENT_GONE': (client_gone, ),
    'ORDER_CLIENT_FUCK': (client_fuck, ),
    'CALLBACK_DELIVERED': (callback_delivered, ),
    'CALLBACK_BUSY': (callback_busy, 'ORDER_CREATED', 'ORDER_COMPLETED', 'ORDER_ABORTED', 'ORDER_CLIENT_FUCK' ),
    'CALLBACK_STARTED': (callback_started, ),
    'CALLBACK_ERROR': (callback_error, 'ORDER_CREATED', 'ORDER_COMPLETED', 'ORDER_ABORTED', 'ORDER_CLIENT_FUCK' ),
    'CALLBACK_TEMPORARY_ERROR': (callback_temporary_error, 'ORDER_CREATED', 'ORDER_COMPLETED', 'ORDER_ABORTED', 'ORDER_CLIENT_FUCK' ),
    'SMS_SENDED': (sms_sended, ),
    'SMS_ERROR': (sms_error, ),
    }
