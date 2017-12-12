#!/usr/bin/python3
import tmtapi.settings as settings
from tmtapi.settings import logger
import tmtapi.tmtapi as tmtapi


async def callback_delivered(event, order_data, ws, loop):
    order_data['request_state'] = settings.CALLBACK_DELIVERED
    await ws.send_json({'SET_REQUEST_STATE': order_data})
    # event, events, order_data = await tmtapi.set_request_state(event, order_data, ws, loop)
    events = []
    return event, events, order_data


async def callback_noanswer(event, order_data, ws, loop):
    order_data['request_state'] = settings.CALLBACK_NOANSWER
    await ws.send_json({'SET_REQUEST_STATE': order_data})
    # event, events, order_data = await tmtapi.set_request_state(event, order_data, ws, loop)
    events = []
    return event, events, order_data


async def callback_busy(event, order_data, ws, loop):
    order_data['request_state'] = settings.CALLBACK_BUSY
    await ws.send_json({'SET_REQUEST_STATE': order_data})
    # event, events, order_data = await tmtapi.set_request_state(event, order_data, ws, loop)
    events = []
    return event, events, order_data


async def callback_started(event, order_data, ws, loop):
    order_data['request_state'] = settings.CALLBACK_STARTED
    await ws.send_json({'SET_REQUEST_STATE': order_data})
    # event, events, order_data = await tmtapi.set_request_state(event, order_data, ws, loop)
    events = []
    return event, events, order_data


async def callback_error(event, order_data, ws, loop):
    order_data['request_state'] = settings.CALLBACK_ERROR
    await ws.send_json({'SET_REQUEST_STATE': order_data})
    # event, events, order_data = await tmtapi.set_request_state(event, order_data, ws, loop)
    events = []
    return event, events, order_data
