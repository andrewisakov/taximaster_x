#!/usr/bin/python3
import websocket
import json
import urllib
import urllib.request
import hashlib
import ssl
import xmltodict
import datetime
import logging
from settings import PORT as port
import tmtapi


def request(url, params, method='GET'):
    req = urllib.request.Request(url, method=method)
    # for header in headers:
    #     req.add_header(header, headers[header])
    # context = ssl._create_unverified_context()
    r = urllib.request.urlopen(req, params.encode() if method == 'POST'\
                               else None).read()
    return r

url = f'http://127.0.0.1:{port}/'
data = dict(name='order_accepted',
            startparam1='9278831370',
            startparam3=1,
            atartparam4=1000001)


params = urllib.parse.urlencode(data)
url += params
params = None
response = request(url, params)
print(response)


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


websocket.enableTrace(True)
ws = websocket.create_connection(f'ws://127.0.0.1:{port}/ws',
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close,
                            on_open=on_open)
# ws.run_forever()

ws.send(json.dumps({'SUBSCRIBE': ('ORDER_CREATED', 'ORDER_COMPLETED',)}))
ws.send(json.dumps({'UNSUBSCRIBE': ()}))
