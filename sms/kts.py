#!/usr/bin/python3
import asyncio
import aiohttp
import json
import requests
from requests.auth import HTTPDigestAuth
import xmltodict
import time
# import sms.settings as settings
import settings
from settings import logger


async def request_channel(address, cmd, login='user', passwd='user', realm='kts_voip', data=None):
    url = 'http://%s/%s' % (address, cmd)
    if data is None:
        response = requests.get(url, auth=HTTPDigestAuth(
            login, passwd), verify=False, stream=True)
    else:
        response = requests.post(url, auth=HTTPDigestAuth(
            login, passwd), verify=False, stream=True, data=data)
    logger.debug(f'{response.content}')

    return response


async def get_channels(address, login='user', passwd='user', realm='kts_voip'):
    channels = await request_channel(address, 'json?a=chlist', login, passwd, realm)
    ok, channels = channels.ok, channels.json()
    # print(ok, channels)
    if channels['message'] == 'ok':
        channels__ = {}
        for ch in channels['channel']:
            channels__[int(ch['num'])] = {'enabled': (ch['enabled'] == 1),
                                          'creg': (ch['creg'].upper().find('REGISTERED') > 0),
                                          'operator': (ch['op']),
                                          'present': (ch['present'] == 1),
                                          'lac': ch['lac'],
                                          'sig': ch['sig'],
                                          }
        channels = channels__
        channels['message'] = 'ok'
    return ok, channels


async def get_channel(address, ch, login='user', passwd='user', realm='kts_voip'):
    ok, channels = await get_channels(address, login, passwd, realm)
    # print('get_channel: %s' % channels)
    if channels['message'] == 'ok':
        try:
            channel = channels[ch]
        except Exception as e:
            print(e)
            channel = {'enabled': False,
                       'num': ch,
                       'creg': False,
                       'operator': '',
                       'lac': -1,
                       'sig': -1000,
                       'present': False, }
    else:
        channel = {}
    # print(ok, channel)
    return ok, channel


async def get_logs(address, login='user', passwd='user', realm='kts_voip'):
    logs = await request_channel(address, 'xml?a=getlogs', )
    logs_text = json.loads(json.dumps(xmltodict.parse(logs.text)))
    # print(logs.ok, logs_text)
    return logs.ok, logs_text


async def get_smslist(address, login='user', passwd='user', realm='kts_voip'):
    smslist = await request_channel(address=address,
                                    cmd='json?a=smslist',
                                    login=login,
                                    passwd=passwd,
                                    realm=realm
                                    )
    ok, smslist = smslist.ok, smslist.json() if smslist.ok else {}
    print(ok, smslist)
    return ok, smslist


async def del_sms(address, sms_id=None, login='user', passwd='user', realm='kts_voip'):
    result = await request_channel(address=address,
                                   login=login,
                                   passwd=passwd,
                                   realm=realm,
                                   cmd='xml?a=delallsms' +
                                       f'&id={sms_id}' if isinstance(
                                           sms_id, (int,)) else '')
                                   # TODO: Разобрать result
    ok, result = result.ok, result.text
    print(ok, result)


async def set_time(address, login='user', passwd='user', realm='kts_voip'):
    result = await request_channel(address=address,
                                   login=login,
                                   passwd=passwd,
                                   realm=realm,
                                   cmd='index?a=settime',
                                   data={'ts': str(int(time.time()))})
    ok, result = result.ok, result.json()
    print(ok, result)
    return ok, result


async def send_sms(address, ch, phone, message, login='user', passwd='user', realm='kts_voip', is_flush=False):
    result = await request_channel(address=address,
                                   login=login,
                                   passwd=passwd,
                                   realm=realm,
                                   cmd='sendsms',
                                   data={'from': 'Народное',
                                         'ch': ch,
                                         'is_flush': 1 if is_flush else 0,
                                         'phone': phone,
                                         'text': message})
    # print(f'{result.ok}, {result.reason}')
    return result.ok, result.reason


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(send_sms(address='127.0.0.1:8480',
                                    #  channel=4, phone='+79024395996',
                                    #  message='Проверка асинк'))
    # loop.run_until_complete(get_channel(address='127.0.0.1:8480', ch=4))
    loop.run_until_complete(set_time(address='127.0.0.1:8480'))
    loop.stop()
    loop.close()
