#!/usr/bin/python3
import os
import aiohttp
import asyncio
# from tmtapi.oktell import *
from tmtapi.drivers import *
from tmtapi.callbacks import *
import tmtapi.settings as settings
# import websocket_cli as wscli
from tmtapi.settings import logger
import tmtapi.database as database
import tmtapi.tmtapi as tmtapi


orders = {}
cars = {}


def event_result(future):
    """Событие обработано, дальнейшие действия"""
    event, events, order_data = future.result()
    print(f'event_result: {event}, {events}, {order_data}')

    if event in ('ORDER_COMPLETED', 'ORDER_ABORTED'):
        del orders[order_data['order_id']]
    logger.info(f'{event}, {events}, {order_data}')


async def set_request_state(event, order_data, ws, loop):
    events = []
    api_result = await tmtapi.api_request(
        ('set_request_state',
            {'order_id': order_data['order_id'],
             'state': order_data['request_state'],
             'phone_type': 1,
             'state_id': 0,
             }, ))
    return event, events, order_data


async def get_order_data(event, order_data, ws, loop):
    order_state = await tmtapi.api_request(
        ('get_order_state',
            {'order_id': order_data['order_id']})
    )
    logger.info(order_state)
    order_info = await tmtapi.api_request(
        ('get_info_by_order_id',
            {'order_id': order_data['order_id'],
                'fields': ('DRIVER_TIMECOUNT-SUMM-SUMCITY-'
                           'DISCOUNTEDSUMM-SUMCOUNTRY-SUMIDLETIME-CASHLESS-'
                           'CLIENT_ID-FROMBORDER-DRIVER_PHONE-CREATION_WAY').lower(), })
    )
    logger.info(f'{order_info}')
    order_info = order_info['data']
    # Консолидировать подробности по заказу
    order_info.update(order_state)
    order_info['phones'] = (order_info['phone_to_callback'][-10:], )
    # del order_info['phone_to_callback']
    logger.info(order_info)
    events = []
    return event, events, order_info


async def created(event, order_data, ws, loop):
    events = []
    await set_request_state(event, order_data, ws, loop)
    await ws.send_json({'ORDER_CREATED': order_data, })
    return event, events, order_data


async def accepted(event, order_data, ws, loop):
    events = []
    await set_request_state(event, order_data, ws, loop)
    event, events, order_data = await get_order_data(event, order_data, ws, loop)
    # Сформировать voip/sms сообщения
    order_data.update(messages=(await database.get_voip_message(order_data),
                                await database.get_sms_message(order_data)))
    await ws.send_json({'ORDER_ACCEPTED': order_data, })
    return event, events, order_data


async def completed(event, order_data, ws, loop):
    events = []
    await set_request_state(event, order_data, ws, loop)
    # Сформировать СМС с отчётом
    order_data.update(messages=(await database.get_voip_message(order_data),
                                await database.get_sms_message(order_data)))
    await ws.send_json({'ORDER_COMPLETED': order_data, })
    return event, events, order_data


async def aborted(event, order_data, ws, loop):
    events = []
    await set_request_state(event, order_data, ws, loop)
    await ws.send_json({'ORDER_ABORTED': order_data, })
    return event, events, order_data


async def client_gone(event, order_data, ws, loop):
    events = []
    await set_request_state(event, order_data, ws, loop)
    # Сформировать voip/sms сообщения
    order_data.update(messages=(await database.get_voip_message(order_data),
                                await database.get_sms_message(order_data)))
    await ws.send_json({'ORDER_CLIENT_GONE': order_data, })
    return event, events, order_data


async def client_fuck(event, order_data, ws, loop):
    events = []
    await set_request_state(event, order_data, ws, loop)
    await ws.send_json({'ORDER_CLIENT_FUCK': order_data, })
    return event, events, order_data


async def offered_driver(event, order_data, ws, loop):
    events = []
    await set_request_state(event, order_data, ws, loop)
    await ws.send_json({'ORDER_OFFERED_DRIVER': order_data, })
    return event, events, order_data


async def no_cars(event, order_data, ws, loop):
    events = []
    await set_request_state(event, order_data, ws, loop)
    # Сформировать voip/sms сообщения
    order_data.update(messages=(await database.get_voip_message(order_data),
                                await database.get_sms_message(order_data)))
    await ws.send_json({'ORDER_NO_CARS': order_data, })
    return event, events, order_data


async def no_cars_aborted(event, order_data, ws, loop):
    events = []
    await set_request_state(event, order_data, ws, loop)
    await ws.send_json({'ORDER_NO_CARS_ABORTED': order_data, })
    return event, events, order_data


async def tmabconnect(event, order_data, ws, loop):
    events = []
    await ws.send_json({'CALLBACK_BRIDGE_START': order_data, })
    return event, events, order_data


EVENTS = {
    'OKTELL_ORDER_CREATED': (created, ),
    'OKTELL_ORDER_ACCEPTED': (accepted, ),
    'OKTELL_ORDER_COMPLETED': (completed, ),
    'OKTELL_ORDER_ABORTED': (aborted, ),
    'OKTELL_ORDER_CLIENT_GONE': (client_gone, ),
    'OKTELL_ORDER_CLIENT_FUCK': (client_fuck, ),
    'OKTELL_ORDER_OFFERED_DRIVER': (offered_driver, ),
    'OKTELL_ORDER_NO_CARS': (no_cars, ),
    'OKTELL_ORDER_NO_CARS_ABORTED': (no_cars, ),
    'OKTELL_TMABCONNECT': (tmabconnect, ),
    'SET_REQUEST_STATE': (set_request_state, ),
    'CALLBACK_ORIGINATE_DELIVERED': (callback_delivered, ),
    'CALLBACK_ORIGINATE_NOANSWER': (callback_noanswer, ),
    'CALLBACK_ORIGINATE_BUSY': (callback_busy, ),
    'CALLBACK_ORIGINATE_STARTED': (callback_started, ),
    'CALLBACK_ORIGINATE_ERROR': (callback_error, ),
    'CALLBACK_ORIGINATE_TEMPORARY_ERROR': (callback_error, ),
    # 'SMS_SENDED': (sms_sended, ),
    # 'SMS_ERROR': (sms_error, ),
    'GET_ORDER_DATA': (get_order_data, ),
    # 'DRIVER_OPER_CREATE': (driver_oper_create, ),
    # 'DRIVER_OPER_OPDATE': (driver_oper_update, ),
    'DRIVER_TERM_OPER_CREATE': (driver_term_oper_create, ),
    'DRIVER_TERM_OPER_UPDATE': (driver_term_oper_update, ),
}
