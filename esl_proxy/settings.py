#!/usr/bin/python3
import os
import pwd
import grp
import logging
import logger as logger_

ESL_SERVER = ('127.0.0.1', 8021)

APP_DIR = os.path.dirname(__file__)

ESL_PROXY = {'host': '0.0.0.0', 'port': 28021}
log_file = os.path.join(APP_DIR, 'esl_proxy.log')
logger = logger_.rotating_log(log_file, 'esl_proxy', log_level=logging.DEBUG)
MAX_CALLBACKS = 128
ESLLogin = (b'127.0.0.1', b'8021', b'ClueCon')
ESL_TIMEOUT = 20
VOIP_USER = (pwd.getpwnam('andrew').pw_uid, grp.getgrnam('andrew').gr_gid)
SIMPLE_CALLBACK = '6700'
PID = os.path.join(APP_DIR, 'esl_proxy.pid')
