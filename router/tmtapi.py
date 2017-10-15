#!/usr/bin/python3
import asyncio
import hashlib
from settings import TMAPI
from settings import logger


@asyncio.coroutine
def order_create(order_data):
    request = {
               'PHONE': order_data['calleeid'],
               'ORDER_STATE_ID': 1,
               'CREWGROUPID': '<Группа «Рация»>',
               'TARIF_ID': '<Тариф>',
               'STARTUSER': '<service_name_id>',
               'PHONE_TO_DIAL': order_data['callerid'],
               'FROMBORDER': 1,
               'INPUTTIME': datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
              }

    return order_data


# @asyncio.coroutine
async def signature(data):
    # генератор подписи
    logger.debug ('http_tmapi.signature generator')
    return hashlib.md5((data+TMAPI['sign']).encode()).hexdigest()


# @asyncio.coroutine
async def request(url, headers, params, method):
    req = await urllib.request.Request(url, method=method)
    for header in headers:
        req.add_header(header, headers[header])
    context = ssl._create_unverified_context()
    if method == 'POST':
        r = urllib.request.urlopen(req, params.encode(), context=context)
        r = await r.read()
    else:  # GET
        r = urllib.request.urlopen(req, context=context)
        r = await r.read()
    return r


async def inline_request(request, api, data, method='GET'): # urlencoded запрос
    params = ''
    host, port = TMAPI['host'], TMAPI['post']
    url = f'https://{host}:{port}/{api[0]}/{api[1]}/{request}'
    params = urllib.parse.urlencode(data)
    signature_ = await signature(params)
    headers = {
               'Signature': signature_,
               'Content-Type': 'application/x-www-form-urlencoded',
              }
    if request in inline_sign:
        params += '&signature=%s' % signature_
    if method == 'GET':
        url += '?'+params
        params = None
    response = await request(url, headers, params, method)
    # print ('inline_request: %s' % response)
    try:  # Результат в json?
        response = json.loads(response.decode())
    except:  # Значит, в xml. ПЕреводим в json
        try:
            response = json.loads(json.dumps(xmltodict.parse(response.lower())))
            response = response['response']
            logger.debug('http_tmapi.inline_request.response (%s)' % response)
        except Exception as e:
            logger.error('ERROR http_tmapi.inline_request %s -- %s -> %s ' % (e, request, response))
    try:
        for r in response['data']:  # Конвертация 'ГГГГММДДЧЧММСС' в datetime
            try:
                if len(response['data'][r]) == 14:
                    response['data'][r] = datetime.datetime.strptime(response['data'][r], '%Y%m%d%H%M%S')
            except Exception as e:
                pass
    except:
        pass
    return response


# @asyncio.coroutine
async def json_request(request, api, post_data, method='POST'): # json запрос
    post_data = json.dumps(post_data)
    host, port = settings.TMAPI['host'], settings.TMAPI['post']
    url = f'https://{host}:{port}/{api[0]}/{api[1]}/{request}'
    headers = {
               'Signature': await signature(post_data),
               'Content-Type': 'application/json',
              }
    return await json.loads(request(url, headers, post_data, method).decode())


requests = {
    'set_request_state': ('POST', 'tm_tapi', '1.0', inline_request, 'XML'),
    'create_driver_operation': ('POST', 'common_api', '1.0', json_request, ''),
    'save_client_feed_back': ('POST', 'common_api', '1.0', json_request, ''),
    'ping': ('GET',  'common_api', '1.0', inline_request),
    'get_finished_orders': ('GET', 'common_api', '1.0', inline_request),
    'get_drivers_info': ('GET', 'common_api', '1.0', inline_request),
    'get_driver_info': ('GET', 'common_api', '1.0', inline_request),
    'get_order_state': ('GET', 'common_api', '1.0', inline_request),
    'check_authorization': ('GET', 'common_api', '1.0', inline_request),
    'get_car_info': ('GET', 'common_api', '1.0', inline_request),
    'get_crew_groups_list': ('GET', 'common_api', '1.0', inline_request),
    'get_crews_info': ('GET', 'common_api', '1.0', inline_request),
    'get_tariffs_list': ('GET', 'common_api', '1.0', inline_request),
    'get_services_list': ('GET', 'common_api', '1.0', inline_request),
    'get_discounts_list': ('GET', 'common_api', '1.0', inline_request),
    # 'change_order_state': ('POST', 'common_api', '1.0', inline_request),
    'create_order2': ('POST', 'common_api', '1.0', json_request),
    'get_current_orders': ('GET', 'common_api', '1.0', inline_request),
    'get_info_by_order_id': ('GET', 'tm_tapi', '1.0', inline_request),
    'change_order_state': ('POST', 'tm_tapi', '1.0', inline_request),
}


def api_request(data):  # Точка входа в запрос
    # global NEED_DEBUG
    logger.debug('http_tmapi.api_request: %s' % data)
    command = data[0].lower()
    params = data[1]

    method = requests[command][0].upper()
    api = (requests[command][1].lower(), requests[command][2])
    func = requests[command][3]
    result = func(command, api, params, method)
    return result
