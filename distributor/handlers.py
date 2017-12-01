import datetime
import json
# import asyncio
from aiohttp import web
from settings import logger
import settings
import database


def json_serial(self, data):
    if isinstance(data, (datetime.datetime, tuple)):
        return data.__str__()
    return data


async def drop_cache(request):
    with (await database.distributors_cache_semaphore), (await database.distributors_semaphore):
        database.distributors = {}
        database.distributors_cache = {}
    return web.Response(status=200, text='OK')


async def show_cache(request):
    with (await database.distributors_cache_semaphore):
        # print(database.distributors_cache)
        response = {f'{k[0]} {k[1]} {k[2]}': {'name': v[0], 'cut': v[1], 'id': v[2]} for k, v in database.distributors_cache.items()}
    return web.Response(status=200, text=json.dumps(response), content_type='application/json')


async def smsc(request):
    """ Запрос СМС шлюза """
    pool = request.app['postgres']
    phone = request.match_info['phone'][-10:]
    response = '{}'
    if (len(phone) == max(settings.PHONE_LENGTH)) and (phone[0] == '9'):
        smsc, channel, sended, phone = await database.select_smsc(phone, pool)
        response = {'phone': phone, 'smsc': smsc, 'channel': channel, 'sended': sended}
    return web.Response(status=200, text=json.dumps(response), content_type='application/json')


async def distributor(request):
    response = '{}'
    pool = request.app['postgres']
    phone = request.match_info['phone'][-10:]
    lock = int(request.match_info['lock']) != 0
    if len(phone) in settings.PHONE_LENGTH:
        distributor, phone = await database.select_distributor(phone, pool)
        if lock:
            await database.distributors[distributor].acquire()
        response = {'phone': phone, 'distributor': distributor, 'locked': lock}
    return web.Response(status=200, text=json.dumps(response), content_type='application/json')


async def distributor_unlock(request):
    distributor = request.match_info['distributor'].lower()
    response = {'distributor': distributor}
    if distributor in database.distributors.keys():
        database.distributors[distributor].release()
        response.update({'result': 0, 'state': database.distributors[distributor].locked()})
    else:
        response.update({'result': 1})
    return web.Response(status=200, text=json.dumps(response), content_type='application/json')
