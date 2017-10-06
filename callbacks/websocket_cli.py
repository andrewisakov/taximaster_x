#!/usr/bin/python3
import asyncio
import logging
import websocket
import handlers
import settings
from settings import logger


queue = asyncio.Queue()


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

