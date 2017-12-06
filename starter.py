#!/usr/bin/python3
# import argparse
import sys
# import datetime
# import psycopg2
import asyncio
import aiohttp


params = ('orders', 'callbacks', 'sms', 'tmtapi')
service_name = ''


def exception_handler(loop, context):
    print(context)


async def main(loop):
    active = True
    while active:
        try:
            session = aiohttp.ClientSession()
            async with session.ws_connect(url=settings.WS_SERVER) as ws:
                # logger.debug(ws)
                await ws.send_json({'SUBSCRIBE': tuple(handlers.EVENTS.keys())})
                while True:
                    events = await ws.receive_json()
                    for ev, order_data in events.items():
                        ev = ev.upper()
                        logger.debug(ev, order_data)
                        if ev == f'STOP_{service_name}':
                            active = False
                            break

                        order_data.update(order_state=ev)

                        if order_data['order_id'] not in handlers.orders.keys():
                            # Важно, чтобы события выполнялись в порядке поступления, без гонки
                            handlers.orders[order_data['order_id']] = {
                                'semaphore': asyncio.BoundedSemaphore(1),
                                'events': []}
                        task = loop.create_task(
                            handlers.EVENTS[ev][0](ev, order_data, ws, loop))
                        task.add_done_callback(handlers.event_result)
                    if not active:
                        break
                await ws.send_json({'UNSUBSCRIBE': tuple(handlers.EVENTS.keys())})
            session.close()
        except Exception as e:
            logger.error(e.__str__())
            await asyncio.sleep(settings.WS_TIMEOUT)

    await asyncio.sleep(3)


if __name__ == '__main__':
    _exit = False
    print(sys.argv)
    if (len(sys.argv) != 1) and (sys.argv[1] in params):
        service_name = sys.argv[1].upper()
        if sys.argv[1] == 'orders':
            from orders.settings import logger
            from orders import settings
            from orders import handlers
        elif sys.argv[1] == 'callbacks':
            from callbacks.settings import logger
            from callbacks import settings
            from callbacks import handlers
        elif sys.argv[1] == 'sms':
            from sms.settings import logger
            from sms import settings
            from sms import handlers
        elif sys.argv[1] == 'tmtapi':
            from tmtapi.settings import logger
            from tmtapi import settings
            from tmtapi import handlers
        else:
            _exit = True
    else:
        _exit = True
    if _exit:
        print('starter.py orders|callbacks|sms|tmtapi')
        sys.exit(1)
    logger.info('Запуск')
    loop = asyncio.get_event_loop()
    # future = asyncio.Future()
    task = loop.run_until_complete(main(loop))
    loop.stop()
    loop.close()
    # loop.run_forever()
    logger.info('завершение')
