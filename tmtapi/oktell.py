#!/usr/bin/python3
import tmtapi.settings as settings
from tmtapi.settings import logger
import tmtapi.tmtapi as tmtapi


async def created(event, order_data, ws, loop):
    events = []
    await set_request_state(event, order_data, ws, loop)
    await ws.send_json({'ORDER_CREATED': order_data, })
    return event, events, order_data


async def accepted(event, order_data, ws, loop):
    events = []
    await set_request_state(event, order_data, ws, loop)
    event, events, order_data = await get_order_data(event, order_data, ws, loop)
    # TODO: Сформировать voip/sms сообщения
    await ws.send_json({'ORDER_ACCEPTED': order_data, })
    return event, events, order_data


async def completed(event, order_data, ws, loop):
    events = []
    await set_request_state(event, order_data, ws, loop)
    # TODO: сформировать СМС с отчётом
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
    # TODO: Сформировать voip/sms сообщения
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
    # TODO: Сформировать voip/sms сообщения
    await ws.send_json({'ORDER_NO_CARS': order_data, })
    return event, events, order_data


async def no_cars_aborted(event, order_data, ws, loop):
    events = []
    await set_request_state(event, order_data, ws, loop)
    await ws.send_json({'ORDER_NO_CARS_ABORTED': order_data, })
    return event, events, order_data
