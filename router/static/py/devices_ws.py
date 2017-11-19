from browser import document as doc
from browser import websocket, window, console
import time
import json


def gsm_unregistered(data):
    # print('gsm_unregistered: %s' % data)
    pass


def gsm_registered_home(data):
    # print('gsm_registered_home: %s' % data)
    pass


def gsm_search(data):
    # print('gsm_search: %s' % data)
    pass


def gsm_registration_locked(data):
    # print('gsm_registration_locked: %s' % data)
    pass


def gsm_registered_unknown(data):
    # print('gsm_registered_unknown: %s' % data)
    pass


def gsm_registered_roaming(data):
    # print('gsm_registered_roaming: %s' % data)
    pass


def sms_incoming(data):
    # print('sms_incoming: %s' % data)
    pass


def sms_broadcast(data):
    # print('sms_broadcast: %s' % data)
    pass


def sms_delivered(data):
    # print('sms_delivered: %s' % data)
    pass


def sms_unknown(data):
    # print('sms_unknown: %s' % data)
    pass


def sip_incoming(data):
    # print('sip_incoming: %s' % data)
    pass


def sip_invite(data):
    # print('sip_invite: %s' % data)
    pass


def sip_early(data):
    # print('sip_early: %s' % data)
    pass


def sip_connecting(data):
    # print('sip_connecting: %s' % data)
    pass


def sip_confirmed(data):
    # print('sip_confirmed: %s' % data)
    pass


def sip_disconnected(data):
    # print('sip_disconnected: %s' % data)
    pass


EVENTS = {'GSM_UNREGISTERED': gsm_unregistered,
          'GSM_REGISTERED_HOME': gsm_registered_home,
          'GSM_SEARCH': gsm_search,
          'GSM_REGITRATION_LOCKED': gsm_registration_locked,
          'GSM_REGISTERED_UNKNOWN': gsm_registered_unknown,
          'GSM_REGISTERED_ROAMING': gsm_registered_roaming,
          'SMS_INCOMING': sms_incoming,
          'SMS_BROADCAST': sms_broadcast,
          'SMS_DELIVERED': sms_delivered,
          'SMS_UNKNOWN': sms_unknown,
          'SIP_INCOMING': sip_incoming,
          'SIP_INVITE': sip_invite,
          'SIP_EARLY': sip_early,
          'SIP_CONNECTING': sip_connecting,
          'SIP_CONFIRMED': sip_confirmed,
          'SIP_DISCONNCTED': sip_disconnected, }


ws = None


def _subscribe(ev=None):
    print({'SUBSCRIBE': tuple(EVENTS.keys())})
    subscribe_json = json.dumps({'SUBSCRIBE': tuple(EVENTS.keys())})
    ws.send(subscribe_json)


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
    subscribe_json = json.dumps({'SUBSCRIBE': tuple(EVENTS.keys())})
    ws.send(subscribe_json)


def on_message(ev):
    # message reeived from server
    for event, data in json.loads(ev.data).items():
        # print("Message %s received : %s" % (event, data))
        EVENTS[event](data)


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
