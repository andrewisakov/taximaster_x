#!/usr/bin/python3
import os
import logger as logger_

WS_SERVER = '127.0.0.1'

APP_DIR = os.path.dirname(__file__)
SQL_DIR = os.path.join(APP_DIR, 'sql')
logger = logger_.rotating_log(os.path.join(APP_DIR, 'callbacks.log'))
DNS = 'dbname=taximaster user=taximaster password=taximaster host=192.168.0.100'
