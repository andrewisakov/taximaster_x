#!/usr/bin/python3
import os
# import logging
import asyncio
import psycopg2 as pg2
import asyncpg
import sms.settings as settings
# import websocket_cli as wscli
# import callbacks.freeswitch
# import database
from sms.settings import logger
import sms.kts as kts


orders = {}
db = pg2.connect(settings.DNS)


def event_result(future):
    """Событие обработано, дальнейшие действия"""
    event, events, bridge_data = future.result()
    print(f'event_result: {event}, {events}, {bridge_data}')
    # TODO: Отправка events в websocket

    logger.info(f'{event}, {events}, {bridge_data}')


@asyncio.coroutine
def select_distributor(phone):
    address, channel = '0', 0
    return address, channel


@asyncio.coroutine
def send_sms(event, bridge_data, ws, loop):
    address, channel = await select_distributor(bridge_data['phones'][0])
    result = await kts.send_sms(address, channel, bridge_data['phones'][0], bridge_data['message'])
    # TODO: Записать в БД
    events = []
    return event, events, bridge_data


@asyncio.coroutine
def sms_delivered(event, bridge_data, ws, loop):
    # TODO: Записать в БД
    events = []
    return event, events, bridge_data


EVENTS = {
    'SEND_SMS': (send_sms,),
    'SMS_DELIVERED': (sms_delivered,)
}
