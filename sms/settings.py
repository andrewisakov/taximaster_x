#!/usr/bin/python3
import os
# import logging
import logger as logger_

WS_SERVER = 'ws://127.0.0.1:4055/ws'
WS_TIMEOUT = 10

APP_DIR = os.path.dirname(__file__)
SQL_DIR = os.path.join(APP_DIR, 'sql')
logger = logger_.rotating_log(os.path.join(
    APP_DIR, 'sms.log'), 'sms_log')
DNS = ('dbname=50eb8a3c0e444176ea5139ad5de941cd79daa8b9 user=freeswitch '
       'password=freeswitch host=127.0.0.1 port=15432')
# FREESWITCH_ESL = {'host': '127.0.0.1', 'port': 28021}
LOCAL_CODE = '8362'
PHONE_LENGTH = (6, 10)
