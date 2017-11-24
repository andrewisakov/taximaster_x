import json
import asyncio
import aiohttp
# import tornado.log
# import tornado.web
# from tornado import gen
# from tornado.queues import Queue
# import tornado.escape
# from tornado.escape import json_encode
# from tornado.escape import json_decode
from settings import logger
import settings
import database
# import websocket_cli as wscli
# from settings import logger


class SMSC(tornado.web.RequestHandler):
    # def check_xsrf_cookie(self):
    #     pass

    def json_serial(self, data):
        if isinstance(data, (datetime.datetime, )):
            return data.__str__()
        return data

    @gen.coroutine
    def get(self, request):
        phone = request[-10:]
        # tornado.log.logging.info(f'smsc {phone} {len(phone)} {max(settings.PHONE_LENGTH)}')
        self.set_header("Content-Type", "application/json")
        if (len(phone) == max(settings.PHONE_LENGTH)) and (phone[0] == '9'):
            # tornado.log.logging.info(f'{phone}')
            smsc, channel, sended, phone = await database.get_smsc(phone)
            # phone = f'{settings.REGIO_CODE}{phone}'
            self.write(json_encode({'phone': phone, 'smsc': smsc, 'channel': channel, 'sended': sended}))
        else:
            self.write('')


class Distributor(tornado.web.RequestHandler):
    # def check_xsrf_cookie(self):
    #     pass

    def json_serial(self, data):
        if isinstance(data, (datetime.datetime, )):
            return data.__str__()
        return data

    @gen.coroutine
    def get(self, request):
        # uri = tornado.escape.url_unescape(self.request.uri)
        # tornado.log.logging.info(f'{uri}')
        phone = request[-10:]
        self.set_header("Content-Type", "application/json")
        if len(phone) in settings.PHONE_LENGTH:
            distributor, phone = await database.get_distributor(phone)
            # phone = f'{settings.REGIO_CODE}{phone}'
            self.write(json_encode({'phone': phone, 'distributor': distributor}))
        else:
            self.write('')
