#!/usr/bin/python3
import os
# import logging
import asyncio
import aiohttp
from distributor import database as distributor_
from distributor import settings as distributor_settings
# import distributor.settings as distributor_settings
import callbacks.settings as settings
from callbacks.settings import logger
import callbacks.freeswitch as freeswitch


orders = {}


def event_result(future):
    """Событие обработано, дальнейшие действия"""
    event, events, bridge_data = future.result()
    print(f'event_result: {event}, {events}, {bridge_data}')
    # TODO: Отправка events в websocket

    logger.info(f'{event}, {events}, {bridge_data}')


@asyncio.coroutine
def select_distributor(phone):
    with (yield from aiohttp.ClientSession()) as client:
        with (yield from client.get(f'{settings.DISTRIBUTOR}/distributor/{phone}/1')) as resp:
            distributor = yield from resp.json()
            phone = distributor['phone'] if distributor else None
            distributor = distributor['distributor'] if distributor else None
    return distributor, phone


@asyncio.coroutine
def callback_start(event, bridge_data, ws, loop):
    phone = bridge_data['phones'][0][-10:]
    events = []
    if len(phone) in distributor_settings.PHONE_LENGTH:
        distributor, phone = yield from select_distributor(phone)
        logger.info(f'{phone} {distributor}')
        if distributor or phone:
            bridge_data.update(distributors=(distributor, ))
            bridge_data.update(phones=(phone, ))
            events = ['CALLBACK_ORIGINATE_STARTED', ]
            task = loop.create_task(freeswitch.bridge_start(bridge_data, ws, loop))
            task.add_done_callback(freeswitch.callback_done)
            yield from ws.send_json({'CALLBACK_ORIGINATE_STARTED': bridge_data, })
    return event, events, bridge_data


@asyncio.coroutine
def callback_bridge_start(event, bridge_data, ws, loop):
    events = []
    bridge_data['distributors'] = tuple()
    phones, bridge_data['phones'] = bridge_data['phones'], tuple()
    for phone in phones:
        distributor, phone = yield from select_distributor(phone)
        if distributor and phone:
            bridge_data['distributors'] += (distributor, )
            bridge_data['phones'] += (phone, )
    if len(bridge_data['distributors']) == 2:
        events = ['CALLBACK_BRIDGE_STARTED', ]
        task = loop.create_task(freeswitch.bridge_start(bridge_data, ws, loop))
        task.add_done_callback(freeswitch.callback_done)
        yield from ws.send_json({'CALLBACK_BRIDGE_STARTED': bridge_data, })
    return event, events, bridge_data


def init():
    pass


EVENTS = {
    'CALLBACK_ORIGINATE_START': (callback_start, ),
    'CALLBACK_BRIDGE_START': (callback_bridge_start, ),
    # 'CLEAR_DISTRIBUTORS_CACHE': (clear_distributors_cache, ),
    }
