from browser import document as doc
from browser import websocket, window, console
import time
import json


event_classes = {'gsm_unregistered',
                 'gsm_registered_home',
                 'gsm_search',
                 'gsm_registration_locked',
                 'gsm_registered_unknown',
                 'gsm_registered_roaming',
                 'sms_incoming',
                 'sms_broadcast',
                 'sms_delivered',
                 'sms_unknown',
                 'sip_incoming',
                 'sip_invite',
                 'sip_early',
                 'sip_connecting',
                 'sip_confirmed',
                 'sip_disconnected', }


ws = None


def _open(ev=None):
    if not websocket.supported:
        alert("WebSocket is not supported by your browser")
        return
    global ws
    # open a web socket
    l = window.location
    server_uri = "wss://" if l.protocol == "https:" else "ws://" + \
        l.hostname + ":" + l.port + "/ws"
    ws = websocket.WebSocket(server_uri)
    ws.bind('open', on_open)
    ws.bind('message', on_message)
    ws.bind('close', on_close)
    ws.bind('error', on_error)


def on_error(ev):
    print('WebSocket error')


def on_open(ev):
    # print('WebSocket connected %s' % ev)
    # print(EVENTS)
    subscribe_json = json.dumps({'SUBSCRIBE': tuple(event_classes)})
    ws.send(subscribe_json)


def on_message(ev):
    # message reeived from server
    for event, data in json.loads(ev.data).items():
        el_id = '%s.%s' % (data['header']['address'], data['channel'])
        el = doc.getElementById(el_id)
        _class = set(el.classList) & event_classes
        if _class:
            el.classList.remove(tuple(_class)[0])
        el.classList.add(event.lower())
        # print([c for c in el.classList])


def on_close(ev):
    # websocket is closed
    print("Connection is closed")
    time.sleep(1)
    _open(ev)


# def send(ev):
#     data = doc["data"].value
#     if data:
#         ws.send(data)


_open()
