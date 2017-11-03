#!/usr/bin/python3
import asyncio
import datetime
import pickle
import callbacks.settings as settings
from callbacks.settings import logger
# import websocket_cli as wscli


def callback_done(future):
    order_data, ws = future.result()
    code, data = order_data['result'].split(' ')
    logger.debug(f'freeswitch.originator {code} {data}')
    if code == '-ERR':
        if data == 'USER_BUSY':
            events = ['CALLBACK_ORIGINATE_BUSY', ]
        elif data == 'NO_ANSWER':
            events = ['CALLBACK_ORIGINATE_NOANSWER', ]
        elif data == 'INVALID_GATEWAY':
            events = ['CALLBACK_INVALID_GATEWAY', ]
        elif data == 'NORMAL_TEMPORARY_FAILURE':
            events = ['CALLBACK_ORIGINATE_NORMAL_TEMPORARY_FAILURE', ]
        else:
            events = ['CALLBACK_ORIGINATE_UNKNOWN_ERROR', ]
            order_data['freeswitch_error'] = data
    elif code == '+OK':
        events = ['CALLBACK_ORIGINATE_DELIVERED', ]
    else:
        events = ['CALLBACK_ORIGINATE_UNKNOW_CALLBACK_CODE', ]
        order_data['unknown_callback_code'] = (code, data)

    for ev in events.keys():
        ws.send_json({ev: order_data})
    logger.info(f'callback done {code} {data}')


@asyncio.coroutine
def bridge_start(bridge_data, ws, loop=None):
    reader, writer = yield from asyncio.open_connection(**settings.FREESWITCH_ESL, loop=loop)
    writer.write(pickle.dumps(bridge_data, protocol=2))
    data = yield from reader.read_all()
    order_data = pickle.loads(data)
    writer.close()
    return data, ws
