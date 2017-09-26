#!/usr/bin/python3
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import psycopg2
import asyncio
import websocket
import settings


def rotating_log(path, log_level=logging.INFO):
    # global logger
    logger = logging.getLogger("orders_log")
    logger.setLevel(log_level)

    # add a rotating handler
    formatter = logging.Formatter('%(asctime)s %(module)s [%(lineno)s] %(levelname)s %(message)s')

    handler = TimedRotatingFileHandler(path, when='midnight', backupCount=5)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = rotating_log('orders.log')


def on_message(ws, message):
    print(ws, message)


def on_data(ws, message, data_type, countinue_):
    print(ws, message, data_type, continie_)


def on_error(ws, error):
    print(ws, error)


def on_close(ws):
    print(ws, 'closed...')


def on_open(ws):
    print(ws, 'opened...')


ws = websocket.WebSocketApp(f'ws://{settings.WS_SERVER}/ws',
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close,
                            on_open=on_open)


@asyncio.coroutine
def created(order_data):
    return order_data


@asyncio.coroutine
def completed(order_data):
    return order_data


@asyncio.coroutine
def aborted(order_data):
    return order_data


@asyncio.coroutine
def client_gone(order_data):
    return order_data


@asyncio.coroutine
def client_fuck(order_data):
    return order_data


@asyncio.coroutine
def callback_delivered(order_data):
    return order_data


@asyncio.coroutine
def callback_error(order_data):
    return order_data


@asyncio.coroutine
def callback_started(order_data):
    return order_data


@asyncio.coroutine
def callback_temporary_error(order_data):
    return order_data


@asyncio.coroutine
def sms_sended(order_data):
    return order_data


@asyncio.coroutine
def sms_error(order_data):
    return order_data


def got_result(future):
    # print('got_result', future)
    logger.info('%s %s' % (future.result(), ws))
    # print(future.result(), ws)


EVENTS = {
    'ORDER_CREATED': created,
    # 'ORDER_CREATE': create,
    'ORDER_COMPLETED': completed,
    'ORDER_ABORTED': aborted,
    'ORDER_CLIENT_GONE': client_gone,
    'ORDER_CLIENT_FUCK': client_fuck,
    'CALLBACK_DELIVERED': callback_delivered,
    'CALLBACK_STARTED': callback_started,
    'CALLBACK_ERROR': callback_error,
    'CALLBACK_TEMPORARY_ERROR': callback_temporary_error,
    'SMS_SENDED': sms_sended,
    'SMS_ERROR': sms_error,
    }


async def gen_tests(q):
    # print('gen_tests')
    await q.put(['ORDER_CREATED', {}])
    await q.put(['ORDER_COMPLETED', {}])
    await q.put(['ORDER_ABORTED', {}])
    await q.put(['ORDER_CLIENT_GONE', {}])
    await q.put(['ORDER_CLIENT_FUCK', {}])
    await q.put(['CALLBACK_DELIVERED', {}])
    await q.put(['CALLBACK_STARTED', {}])
    await q.put(['CALLBACK_ERROR', {}])
    await q.put(['CALLBACK_TEMPORARY_ERROR', {}])
    await q.put(['SMS_SENDED', {}])
    await q.put(['SMS_ERROR', {}])
    await q.put(['STOP_ORDERS', {}])


async def main(loop, q):
    while True:
        ev, order_data = await q.get()
        # print(EVENTS[ev.upper()])
        if ev == 'STOP_ORDERS':
            break
        # future = asyncio.Future()
        task = loop.create_task(EVENTS[ev.upper()](order_data))
        task.add_done_callback(got_result)
        # asyncio.ensure_future(EVENTS[ev.upper()]([ev, order_data]), loop=loop)

    # print('tasks', asyncio.tasks.ALL_COMPLETED)
    # print('loop', dir(loop))
    await asyncio.sleep(3)


if __name__ == '__main__':
    # logger = rotating_log('orders.log')
    logger.info('Запуск')
    # print(ws.sock)
    q = asyncio.Queue()
    loop = asyncio.get_event_loop()
    future = asyncio.Future()
    task = loop.create_task(gen_tests(q))
    task = loop.run_until_complete(main(loop, q))
    loop.stop()
    loop.close()
    # loop.run_forever()
    logger.info('завершение')
