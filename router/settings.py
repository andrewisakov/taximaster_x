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


WS_SERVER = f'localhost:{PORT}'
PHONE_SHORT = 6

PG_DSN = 'dbname=50eb8a3c0e444176ea5139ad5de941cd79daa8b9 user=freeswitch password=freeswitch host=localhost port=15432'
