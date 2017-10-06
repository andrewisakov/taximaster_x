#!/usr/bin/python3
import datetime
import psycopg2
import asyncio
# from concurrent.futures import ThreadPoolExecutor
from settings import logger
import websocket_cli as wscli
import settings
import handlers


async def gen_tests(q):
    # print('gen_tests')
    await q.put(['CALLBACK_START', {'id': 100010, 'phones': ('+79278831370', )}])
    await q.put(['CALLBACK_BRIDGE', {'id': 100010, 'phones': ('+79278831370', '+79024395996', )}])
    await q.put(['STOP_CALLBACKS', {}])


def exception_handler(loop, context):
    print(context)


async def main(loop, q):
    # loop.set_exception_handler(exception_handler)
    while True:
        ev, bridge_data = await q.get()
        if ev == 'STOP_CALLBACKS':
            break
        bridge_data.update(event=ev)

        # if bridge_data['id'] not in handlers.callbacks.keys():
        #     handlers.callbacks[order_data['id']] = {
        #         'semaphore': asyncio.BoundedSemaphore(1),
        #         'events': []}
        task = loop.create_task(handlers.EVENTS[ev.upper()][0](ev.upper(), bridge_data))
        task.add_done_callback(handlers.event_result)

    await asyncio.sleep(3)


if __name__ == '__main__':
    # logger = rotating_log('orders.log')
    logger.info('Запуск')
    # print(ws.sock)
    # q = asyncio.Queue()
    loop = asyncio.get_event_loop()
    print(wscli.ws)
    future = asyncio.Future()
    task = loop.create_task(gen_tests(wscli.queue))
    task = loop.run_until_complete(main(loop, wscli.queue))
    loop.stop()
    loop.close()
    # loop.run_forever()
    logger.info('завершение')
