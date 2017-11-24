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
def callback_start(event, bridge_data, ws, loop):
    phone = bridge_data['phones'][0][-10:]
    print(dir())
    if len(phone) in distributor_settings.PHONE_LENGTH:
        # phone = (distributor_settings.LOCAL_CODE + phone) if len(phone) < max(distributor_settings.PHONE_LENGTH) else phone
        distributor, phone = yield from distributor_.get_distributor(phone)
        bridge_data.update(distributors=(distributor, ))
        bridge_data['phones'] = (phone, )
        logger.info(f'{phone} {distributor}')
        with (yield from distributor_.distributors[distributor]):
            events = ['CALLBACK_STARTED', ]
            task = loop.create_task(freeswitch.bridge_start(bridge_data, ws, loop))
            task.add_done_callback(freeswitch.callback_done)
            yield from ws.send_json({'CALLBACK_STARTED': bridge_data, })
        return event, events, bridge_data


@asyncio.coroutine
def callback_bridge_start(event, bridge_data, ws, loop):
    distributor0, phone0 = yield from distributor_.database.get_distributor(phone0)
    distributor1, phone0 = yield from distributor_.database.select_distributor(phone1)
    update.bridge_data(distributors=(distributor0, distributor1))
    update.bridge_data(phones=(phone0, phone1))
    with (yield from distributor_.database.distributors[distributor0]),\
         (yield from distributor_.database.distributors[distributor1]):
        events = ['CALLBACK_BRIDGE_STARTED', ]
        task = loop.create_task(freeswitch.bridge_start(bridge_data, ws, loop))
        task.add_done_callback(freeswitch.callback_done)
        yield from ws.send_json({'CALLBACK_BRIDGE_STARTED': bridge_data, })
    return event, events, bridge_data


def init():
    pass


EVENTS = {
    'CALLBACK_START': (callback_start, ),
    'CALLBACK_BRIDGE_START': (callback_bridge_start, ),
    # 'CLEAR_DISTRIBUTORS_CACHE': (clear_distributors_cache, ),
    }
