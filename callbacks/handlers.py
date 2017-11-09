#!/usr/bin/python3
import os
import logging
import asyncio
import psycopg2 as pg2
import asyncpg
import callbacks.settings as settings
# import websocket_cli as wscli
# import callbacks.freeswitch
# import database
from callbacks.settings import logger
import callbacks.freeswitch as freeswitch


distributors_cache = {('927', 8800000, 8839999): ('megafon', '', 3), }
distributors = {"tele2": asyncio.BoundedSemaphore(3),
                "megafon": asyncio.BoundedSemaphore(2),
                "mts": asyncio.BoundedSemaphore(3),
                "rostelecom": asyncio.BoundedSemaphore(5),
                "inter_city": asyncio.BoundedSemaphore(1),
                "yota": asyncio.BoundedSemaphore(1),
                "beeline": asyncio.BoundedSemaphore(4),
                }
orders = {}


db = pg2.connect(settings.DNS)


def load_distributors():
    SQL = database.get_query('distributors.sql')
    c = yield from db.cursor()
    c.execute(SQL)
    distributors = {dst[0]: asyncio.BoundedSemaphore(
        dst[1]) for dst in c.fetchall()}
    yield from c.close()


@asyncio.coroutine
def select_distributor(phone):
    ARGS = (phone[:3], int(phone[3:]), )
    print(f'select_distributor.distributors_cache: {distributors_cache}, {ARGS}')
    distributor = tuple(d[1] for d in tuple(filter(lambda x:
                                                   (x[0][0] == ARGS[0]) and
                                                   (x[0][1] <= ARGS[1]
                                                    <= x[0][2]),
                                                   distributors_cache.items())))
    print(f'select_distributor.distributor: {distributor}')
    if not distributor:
        SQL = database.get_query('select_distributor.sql')
        c = yield from db.cursor()
        yield from c.execute(SQL, ARGS)
        try:
            distributor, cut_code, distributor_id, a, b = yield from c.fetchone()
            distributors_cache.update(
                {(ARGS[0], a, b): (distributor, cut_code, distributor_id)})
        except:
            distributor, cut_code, distributor_id = 'inter_city', None, 0
        yield from c.close()
    else:
        distributor, cut_code, distributor_id = distributor[0]
    return distributor


@asyncio.coroutine
def clear_distributors_cache(event, bridge_data, ws, loop):
    distributors_cache = {}
    return event, events, bridge_data


def event_result(future):
    """Событие обработано, дальнейшие действия"""
    event, events, bridge_data = future.result()
    print(f'event_result: {event}, {events}, {bridge_data}')
    # TODO: Отправка events в websocket

    logger.info(f'{event}, {events}, {bridge_data}')


@asyncio.coroutine
def callback_start(event, bridge_data, ws, loop):
    if len(bridge_data['phones'][0]) in settings.PHONE_LENGTH:
        bridge_data['phones'][0] = (settings.LOCAL_CODE + bridge_data['phones'][0]) if len(
            bridge_data['phones'][0]) < 10 else bridge_data['phones'][0]
        distributor = yield from select_distributor(bridge_data['phones'][0])
        bridge_data.update(distributors=(distributor, ))
        with (yield from distributors[distributor]):
            events = ['CALLBACK_STARTED', ]
            task = loop.create_task(freeswitch.bridge_start(bridge_data, ws, loop))
            task.add_done_callback(freeswitch.callback_done)
            yield from ws.send_json({'CALLBACK_STARTED': bridge_data, })
        return event, events, bridge_data


@asyncio.coroutine
def callback_bridge_start(event, bridge_data, ws, loop):
    # TODO: Уточнить, кого первым вызывать, кого вторым.
    distributor0 = yield from select_distributor(bridge_data['phones'][0])
    distributor1 = yield from select_distributor(bridge_data['phones'][1])
    update.bridge_data(distributors=(distributor0, distributor1))
    with (yield from distributors[distributor0]), (yield from distributors[distributor1]):
        events = ['CALLBACK_BRIDGE_STARTED', ]
        task = loop.create_task(freeswitch.bridge_start(bridge_data, ws, loop))
        task.add_done_callback(freeswitch.callback_done)
        yield from ws.send_json({'CALLBACK_BRIDGE_STARTED': bridge_data, })
    return event, events, bridge_data


def init():
    distributors = load_distributors()


EVENTS = {
    'CALLBACK_START': (callback_start, ),
    'CALLBACK_BRIDGE_START': (callback_bridge_start, ),
    'CLEAR_DISTRIBUTORS_CACHE': (clear_distributors_cache, ),
    }
