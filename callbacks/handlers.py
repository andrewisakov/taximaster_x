#!/usr/bin/python3
import os
import logging
import asyncio
import psycopg2 as pg2
# import aiopg
import asyncpg
import settings
import websocket_cli as wscli
import freeswitch
from settings import logger


callbacks = {}


def event_result(future):
    """Событие обработано, дальнейшие действия"""
    event, events, bridge_data = future.result()
    print(f'event_result: {event}, {events}, {order_data}, {order_events}')
    # TODO: Отправка events в websocket

    logger.info(f'{event}, {events}, {order_data}, {order_events}')


@asyncio.coroutine
def callback_start(event, bridge_data):
    with (yield from callbacks[bridge_data['id']]['semaphore']):
        # callbacks[bridge_data['id']]['events'].append(order_data)
        events = ['CALLBACK_STARTED']  # Никакого события попрождать не надо
        return event, events, bridge_data


@asyncio.coroutine
def callback_bridge_start(event, bridge_data):
    with (yield from callbacks[bridge_data['id']]['semaphore']):
        # orders[order_data['id']]['events'].append(order_data)
        events = ['CALLBACK_BRIDGE_STARTED']
        return event, events, bridge_data


EVENTS = {
    'CALLBACK_START': (callback_start, ),
    # 'ORDER_CREATE': create,
    'CALLBACK_BRIDGE_START': (callback_bridge, ),
    }
