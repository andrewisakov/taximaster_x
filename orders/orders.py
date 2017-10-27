#!/usr/bin/python3
import datetime
import psycopg2
import asyncio
import aiohttp
import json
# from concurrent.futures import ThreadPoolExecutor
from settings import logger
# import websocket_cli as wscli
import websockets
# from websockets.client import WebSocketClientProtocol
import settings
import handlers


def exception_handler(loop, context):
    print(context)


async def main(loop):
    active = True
    while active:
        try:
            session = aiohttp.ClientSession()
            async with session.ws_connect(url=settings.WS_SERVER) as ws:
                logger.debug(ws)
                await ws.send_json({'SUBSCRIBE': tuple(handlers.EVENTS.keys())})
                while True:
                    events = await ws.receive_json()
                    for ev, order_data in events.items():
                        ev = ev.upper()
                        logger.debug(ev, order_data)
                        if ev == 'STOP_ORDERS':
                            active = False
                            break

                        order_data.update(order_state=ev)

                        if order_data['order_id'] not in handlers.orders.keys():
                            handlers.orders[order_data['order_id']] = {
                                'semaphore': asyncio.BoundedSemaphore(1),
                                'events': []}
                        task = loop.create_task(
                            handlers.EVENTS[ev][0](ev, order_data, ws))
                        task.add_done_callback(handlers.event_result)
                    if not active:
                        break
                await ws.send_json({'UNSUBSCRIBE': tuple(handlers.EVENTS.keys())})
            session.close()
            await asyncio.sleep(settings.WS_TIMEOUT)
        except Exception as e:
            logger.error(e.__str__())

    await asyncio.sleep(3)


if __name__ == '__main__':
    logger.info('Запуск')
    loop = asyncio.get_event_loop()
    # future = asyncio.Future()
    task = loop.run_until_complete(main(loop))
    loop.stop()
    loop.close()
    # loop.run_forever()
    logger.info('завершение')
