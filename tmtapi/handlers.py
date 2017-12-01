#!/usr/bin/python3
import os
import aiohttp
import asyncio
from tmtapi.oktell import *
from tmtapi.drivers import *
from tmtapi.callbacks import *
import tmtapi.settings as settings
# import websocket_cli as wscli
from tmtapi.settings import logger
import tmtapi.database as db
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
            {'order_id': params['order_id']})
    )
    logger.info(order_state)
    order_info = await tmtapi.api_request(
        ('get_info_by_order_id',
            {'order_id': params['order_id'],
                'fields': ('DRIVER_TIMECOUNT-SUMM-SUMCITY-'
                           'DISCOUNTEDSUMM-SUMCOUNTRY-SUMIDLETIME-CASHLESS-'
                           'CLIENT_ID-FROMBORDER-DRIVER_PHONE-CREATION_WAY').lower(), })
    )
    order_info = order_info['data']
    # Консолидировать подробности по заказу
    order_info.update(order_state)
    order_info['phones'] = (order_info['phone_to_callback'][-10:], )
    # del order_info['phone_to_callback']
    logger.info(order_info)
    events = []
    return event, events, order_info


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
    'SET_REQUEST_STATE': (set_rquest_state, )
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
