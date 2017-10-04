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
    await q.put(['ORDER_CREATED', {'id': 100010}])
    await q.put(['ORDER_ACCEPTED', {'id': 100010}])
    await q.put(['ORDER_COMPLETED', {'id': 100010}])
    await q.put(['ORDER_ABORTED', {'id': 100010}])
    await q.put(['ORDER_CLIENT_GONE', {'id': 100010}])
    await q.put(['ORDER_CLIENT_FUCK', {'id': 100010}])
    await q.put(['CALLBACK_DELIVERED', {'id': 100010}])
    await q.put(['CALLBACK_STARTED', {'id': 100010}])
    await q.put(['CALLBACK_ERROR', {'id': 100010}])
    await q.put(['CALLBACK_TEMPORARY_ERROR', {'id': 100010}])
    await q.put(['SMS_SENDED', {'id': 100010}])
    await q.put(['SMS_ERROR', {'id': 100010}])
    await q.put(['STOP_ORDERS', {'id': 100010}])


def exception_handler(loop, context):
    print(context)


async def main(loop, q):
    # loop.set_exception_handler(exception_handler)
    while True:
        ev, order_data = await q.get()
        if ev == 'STOP_ORDERS':
            break
        order_data.update(event=ev)

        if order_data['id'] not in handlers.orders.keys():
            handlers.orders[order_data['id']] = {
                'semaphore': asyncio.BoundedSemaphore(1),
                'events': []}
        task = loop.create_task(handlers.EVENTS[ev.upper()](ev.upper(), order_data))
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
