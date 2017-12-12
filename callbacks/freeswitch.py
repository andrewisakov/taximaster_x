#!/usr/bin/python3
import asyncio
import aiohttp
import datetime
import pickle
import callbacks.settings as settings
from callbacks.settings import logger
# import websocket_cli as wscli


def callback_done(future):
    bridge_data, ws = future.result()
    code, data = bridge_data['result'].split(' ')
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
            bridge_data['freeswitch_error'] = data
    elif code == '+OK':
        events = ['CALLBACK_ORIGINATE_DELIVERED', ]
    else:
        events = ['CALLBACK_ORIGINATE_UNKNOW_CALLBACK_CODE', ]
        bridge_data['unknown_callback_code'] = (code, data)

    for ev in events:
        ws.send_json({ev: bridge_data})
    logger.info(f'callback done {code} {data}')


async def bridge_start(bridge_data, ws, loop):
    reader, writer = await asyncio.open_connection(**settings.FREESWITCH_ESL, loop=loop)
    writer.write(pickle.dumps(bridge_data, protocol=2))
    data = await reader.read()
    bridge_data = pickle.loads(data)
    writer.close()
    logger.info(bridge_data)
    for distributor in bridge_data['distributors']:
        async with aiohttp.ClientSession() as client:
            async with client.get(f'{settings.DISTRIBUTOR}/unlock/{distributor}') as resp:
                distributor_state = await resp.json()
                logger.info(f'{distributor_state}')
    return bridge_data, ws
