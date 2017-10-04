#!/usr/bin/python3
import os
import logging
import asyncio
import psycopg2 as pg2
# import aiopg
import asyncpg
import settings
import websocket_cli as wscli
from settings import logger


LOCKED_EVENTS = {
    'CALLBACK_START': ('ORDER_ABORTED', 'ORDER_COMPLETED'),
    'SMS_SEND': ('ORDER_ABORTED', 'ORDER_COMPLETED'),
}


orders = {}


def event_result(future):
    """Событие обработано, дальнейшие действия"""
    event, events, order_data, order_events = future.result()
    print(f'event_result: {event}, {events}, {order_data}, {order_events}')
    logger.info(f'{event}, {events}, {order_data}')


@asyncio.coroutine
def created(event, order_data):
    """Фиксация события 'ORDER_CREATED'"""
    with (yield from orders[order_data['id']]['semaphore']):
        # print('created:', event, order_data, orders[order_data['id']]['semaphore'])
        orders[order_data['id']]['events'].append(order_data)
        events = []  # Никакого события попрождать не надо
        # print('created:', event, order_data)
        return event, events, order_data, orders[order_data['id']]['events']


@asyncio.coroutine
def completed(event, order_data):
    """Заказ выполнен. Удалить executor для заказа id"""
    with (yield from orders[order_data['id']]['semaphore']):
        orders[order_data['id']]['events'].append(order_data)
        events = []
        # print('completed:', event, order_data)
        return event, events, order_data, orders[order_data['id']]['events']


@asyncio.coroutine
def aborted(event, order_data):
    """Заказ прекоащён. Удалить executor для заказа id"""
    with (yield from orders[order_data['id']]['semaphore']):
        orders[order_data['id']]['events'].append(order_data)
        events = []
        # print('aborted:', event, order_data)
        return event, events, order_data, orders[order_data['id']]['events']


@asyncio.coroutine
def client_gone(event, order_data):
    """Клиент не выходит"""
    with (yield from orders[order_data['id']]['semaphore']):
        orders[order_data['id']]['events'].append(order_data)
        events = ['CALLBACK_START', ]
        # print('client_gone:', event, order_data)
        return event, events, order_data, orders[order_data['id']]['events']


@asyncio.coroutine
def accepted(event, order_data):
    """Заказ принят водителем"""
    with (yield from orders[order_data['id']]['semaphore']):
        orders[order_data['id']]['events'].append(order_data)
        events = ['CALLBACK_START', 'SMS_SEND']
        # print('accepted:', event, order_data)
        return event, events, order_data, orders[order_data['id']]['events']


@asyncio.coroutine
def client_fuck(event, order_data):
    """Клиент не вышел. Удалить executor для заказа id"""
    with (yield from orders[order_data['id']]['semaphore']):
        orders[order_data['id']]['events'].append(order_data)
        events = []
        # print('client_fuck:', event, order_data)
        return event, events, order_data, orders[order_data['id']]['events']


@asyncio.coroutine
def callback_delivered(event, order_data):
    """Отзвон выполнен"""
    with (yield from orders[order_data['id']]['semaphore']):
        orders[order_data['id']]['events'].append(order_data)
        events = []
        # print('callback_delivered:', event, order_data)
        return event, events, order_data, orders[order_data['id']]['events']


@asyncio.coroutine
def callback_error(event, order_data):
    """Ошибка отзвона"""
    with (yield from orders[order_data['id']]['semaphore']):
        orders[order_data['id']]['events'].append(order_data)
        events = ['CALLBACK_START', ]
        # print('callback_error:', event, order_data)
        return event, events, order_data, orders[order_data['id']]['events']


@asyncio.coroutine
def callback_busy(event, order_data):
    """Занято"""
    with (yield from orders[order_data['id']]['semaphore']):
        orders[order_data['id']]['events'].append(order_data)
        events = ['CALLBACK_START', ]
        # print('callback_busy:', event, order_data)
        return event, events, order_data, orders[order_data['id']]['events']


@asyncio.coroutine
def callback_started(event, order_data):
    """Отзвон начат"""
    with (yield from orders[order_data['id']]['semaphore']):
        orders[order_data['id']]['events'].append(order_data)
        events = []
        # print('callback_started:', event, order_data)
        return event, events, order_data, orders[order_data['id']]['events']


@asyncio.coroutine
def callback_temporary_error(event, order_data):
    """Времнная ошибка отзвона. Повторить"""
    with (yield from orders[order_data['id']]['semaphore']):
        orders[order_data['id']]['events'].append(order_data)
        events = ['CALLBACK_START', ]
        # print('callback_temporary_error:', event, order_data)
        return event, events, order_data, orders[order_data['id']]['events']


@asyncio.coroutine
def sms_sended(event, order_data):
    """СМС отправлена"""
    with (yield from orders[order_data['id']]['semaphore']):
        orders[order_data['id']]['events'].append(order_data)
        events = []
        # print('sms_sended:', event, order_data)
        return event, events, order_data, orders[order_data['id']]['events']


@asyncio.coroutine
def sms_error(event, order_data):
    """Ошибка отправки СМС"""
    with (yield from orders[order_data['id']]['semaphore']):
        orders[order_data['id']]['events'].append(order_data)
        events = []
        # print('sms_error:', event, order_data)
        return event, events, order_data, orders[order_data['id']]['events']


EVENTS = {
    'ORDER_CREATED': created,
    # 'ORDER_CREATE': create,
    'ORDER_ACCEPTED': accepted,
    'ORDER_COMPLETED': completed,
    'ORDER_ABORTED': aborted,
    'ORDER_CLIENT_GONE': client_gone,
    'ORDER_CLIENT_FUCK': client_fuck,
    'CALLBACK_DELIVERED': callback_delivered,
    'CALLBACK_BUSY': callback_busy,
    'CALLBACK_STARTED': callback_started,
    'CALLBACK_ERROR': callback_error,
    'CALLBACK_TEMPORARY_ERROR': callback_temporary_error,
    'SMS_SENDED': sms_sended,
    'SMS_ERROR': sms_error,
    }