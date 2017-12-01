#!/usr/bin/python3
import tmtapi.settings as settings
from tmtapi.settings import logger
import tmtapi.tmtapi as tmtapi


async def callback_delivered(event, order_data, ws, loop):
    order_state['request_state'] = settings.CALLBACK_DELIVERED
    event, events, order_data = await set_request_state(event, order_data, ws, loop)
    events = []
    return event, events, order_data


async def callback_noanswer(event, order_data, ws, loop):
    order_state['request_state'] = settings.CALLBACK_NOANSWER
    event, events, order_data = await set_request_state(event, order_data, ws, loop)
    events = []
    return event, events, order_data


async def callback_busy(event, order_data, ws, loop):
    order_state['request_state'] = settings.CALLBACK_BUSY
    event, events, order_data = await set_request_state(event, order_data, ws, loop)
    events = []
    return event, events, order_data


async def callback_started(event, order_data, ws, loop):
    order_state['request_state'] = settings.CALLBACK_STARTED
    event, events, order_data = await set_request_state(event, order_data, ws, loop)
    events = []
    return event, events, order_data


async def callback_error(event, order_data, ws, loop):
    order_state['request_state'] = settings.CALLBACK_ERROR
    event, events, order_data = await set_request_state(event, order_data, ws, loop)
    events = []
    return event, events, order_data
