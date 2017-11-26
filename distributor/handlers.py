import datetime
import json
# import asyncio
from aiohttp import web
from settings import logger
import settings
import database


def json_serial(self, data):
    if isinstance(data, (datetime.datetime, )):
        return data.__str__()
    return data


async def smsc(request):
    # print(request.match_info['phone'])
    pool = request.app['postgres']
    # print(pool)
    phone = request.match_info['phone'][-10:]
    response = '{}'
    if (len(phone) == max(settings.PHONE_LENGTH)) and (phone[0] == '9'):
        smsc, channel, sended, phone = await database.select_smsc(phone, pool)
        response = json.dumps({'phone': phone, 'smsc': smsc, 'channel': channel, 'sended': sended})
    return web.Response(status=200, text=response, content_type='application/json')


async def distributor(request):
    # print(request.match_info['phone'])
    response = '{}'
    pool = request.app['postgres']
    phone = request.match_info['phone'][-10:]
    if len(phone) in settings.PHONE_LENGTH:
        distributor, phone = await database.select_distributor(phone, pool)
        with (await database.distributors[distributor]):
            response = json.dumps({'phone': phone, 'distributor': distributor})
    return web.Response(status=200, text=response, content_type='application/json')
