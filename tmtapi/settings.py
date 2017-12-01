#!/usr/bin/python3
import os
import logger as logger_

WS_SERVER = 'ws://127.0.0.1:4055/ws'
WS_TIMEOUT = 10

APP_DIR = os.path.dirname(__file__)
SQL_DIR = os.path.join(APP_DIR, 'sql')
logger = logger_.rotating_log(os.path.join(APP_DIR, 'tmtapi.log'), 'tmtapi_log')
# PG_DNS = 'dbname=taximaster user=taximaster password=taximaster host=192.168.0.100'
FDB = {'user': 'sysdba', 'password': 'admin',
       'database': 'd:\\tme_db.fdb', 'host': '127.0.0.1',
       'charset': 'win1251'}
FDB_PARALLEL_OPERS = 5
TMAPI = {
    'host': '127.0.0.1',  # ip сервера TM
    'port': 8089,  # порт
    'sign': '1292',  # соль
        }


GOSNUMBER_LENGTH = 3

FAKE_TERM_ACCOUNT = '00000'

CALLBACK_STARTED = 1
CALLBACK_DELIVERED = 2
CALLBACK_BUSY = 3
CALLBACK_NOANSWER = 4
CALLBACK_ERROR = 5
