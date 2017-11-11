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
    pass


@asyncio.coroutine
def send_sms(event, bridge_data, ws, loop):
    return event, events, bridge_data


EVENTS = {'SEND_SMS': (send_sms,),
}