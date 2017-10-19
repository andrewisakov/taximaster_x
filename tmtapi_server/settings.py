#!/usr/bin/python3
import os


PORT = 4055
settings = {
    'cookie_secret': '61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=',
    'login_url': '/login',
    'xsrf_cookies': True,
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


WS_SERVER = f'localhost:{PORT}'
