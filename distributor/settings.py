#!/usr/bin/python3
import os
import logger as logger_


APP_DIR = os.path.dirname(__file__)
SQL_DIR = os.path.join(APP_DIR, 'sql')


PORT = 18021
settings = {
    'cookie_secret': '61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=',
    'login_url': '/login',
    'xsrf_cookies': False,
    'debug': True,
    'autoreload': True,
    'compiled_template_cache': False,
    'serve_traceback': True,
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), "templates"),
    'archive_path': os.path.join(os.path.dirname(__file__), 'static'),
}


TMAPI = {
    'host': '127.0.0.1',  # ip сервера TM
    'port': 8089,  # порт
    'sign': '1292',  # соль
        }


# WS_SERVER = f'localhost:{PORT}'

PG_DSN = 'dbname=50eb8a3c0e444176ea5139ad5de941cd79daa8b9 user=freeswitch password=freeswitch host=localhost port=15432'

LOCAL_CODE = '8362'  # Местные звонки
PHONE_LENGTH = (6, 10)  # Допустимые длины номеров
REGIO_CODE = '+7'  # Выход наружу

logger = logger_.rotating_log(os.path.join(APP_DIR, 'distributor.log'), 'distributor_log')
