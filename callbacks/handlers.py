#!/usr/bin/python3
import os
import logging
import asyncio
import psycopg2 as pg2
import asyncpg
import settings
import websocket_cli as wscli
import freeswitch
import database
from settings import logger


db = pg2.connect(settings.DNS)


distributors = {}


def load_distributors():
    SQL = database.get_query('distributors.sql')
    c = db.cursor()
    c.execute(SQL)
    distributors = {dst[0]: asyncio.BoundedSemaphore(dst[1]) for dst in c.fetchall()}


@asyncio.coroutine
def select_distributor(phone):
    ARGS = (phone[:3], int(phone[3:]), )
    SQL = database.get_query('select_distributor.sql')
    c = yield from db.cursor()
    yield from c.execute(SQL, ARGS)
    try:
        distributor, cut_code, distributor_id = yield from c.fetchone()
    except:
        distributor, cut_code, distributor_id = 'inter_city', None, 0
    yield from c.close()
    return distributor


def event_result(future):
    """Событие обработано, дальнейшие действия"""
    event, events, bridge_data = future.result()
    print(f'event_result: {event}, {events}, {bridge_data}')
    # TODO: Отправка events в websocket

    logger.info(f'{event}, {events}, {bridge_data}')


@asyncio.coroutine
def callback_start(event, bridge_data):
    distributor = yield from select_distributor(bridge_data['phones'][0])
    with (yield from distributors[distributor]):
        events = ['CALLBACK_STARTED']
        return event, events, bridge_data


@asyncio.coroutine
def callback_bridge_start(event, bridge_data):
    # TODO: Уточнить, кого первым вызывать, кого вторым.
    distributor0 = yield from select_distributor(bridge_data['phones'][0])
    distributor1 = yield from select_distributor(bridge_data['phones'][1])
    update.bridge_data(distributors=(distributor0, distributor1))
    with (yield from distributors[distributor0]), (yield from distributors[distributor1]):
        events = ['CALLBACK_BRIDGE_STARTED']
        return event, events, bridge_data


EVENTS = {
    'CALLBACK_START': (callback_start, ),
    'CALLBACK_BRIDGE_START': (callback_bridge, ),
    }
