#!/usr/bin/python3
import os
# import logging
import logger as logger_

WS_SERVER = 'ws://127.0.0.1:4055/ws'
WS_TIMEOUT = 10

APP_DIR = os.path.dirname(__file__)
# SQL_DIR = os.path.join(APP_DIR, 'sql')
logger = logger_.rotating_log(os.path.join(
    APP_DIR, 'kts_snmp.log'), 'kts_snmp_log')


SNMP_IP = '192.168.222.179'
SNMP_PORT = 11162

ROUTER_URL = 'http://127.0.0.1/snmp'
