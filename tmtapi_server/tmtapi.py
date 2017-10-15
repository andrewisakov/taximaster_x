#!/usr/bin/python3
import tornado.log
from tornado import gen
import hashlib
import dicttoxml
import xmltodict
from settings import TMAPI


ORDER_STATES = {
    'order_created': 1,
    'order_aborted': 5,
    'order_completed': 4,
    'order_client_in_car': 11,
    'order_client_gone': 23,
    'order_client_fuck': 12,
    'order_crew_at_place': 10,
    'order_no_cars': 68,
    'order_no_cars_aborted': 6,
    'order_accepted': 7,
    'order_denied_driver': 9,
    }
ORDERS = [{'order_id': 18561, 'state': 1, 'starttime': '', 'finishtime': '',
          'discountsumm': 70.0, 'phone_to_callback': '89278831370', }, ]
CREWS = [{'crew_id': 1, 'car_id': 1, 'driver_id': 1}, ]
CARS = [{'car_id': 1, 'color': 'красный', 'mark': 'ВАЗ', 'model': '2114', 'gosnumber': '515'}, ]
DRIVERS = [{'driver_id': 1, 'term_account': '01181', 'phone': '88001001010', }, ]
CALLBACK_STATES = {'order_callback_accepted', 'order_callback_started', 'order_callback_delivered',
                   'order_callback_busy', 'order_callback_no_answer', 'order_callback_error'}

async def get_info_by_order_id(**kwargs):
    order_data = kwargs
    if 'FIELDS' in params.keys():
        params['FIELDS'] = tuple([f for f in params['FIELDS'].split('-')])
    order_id = order_data['ORDER_ID']
    tornado.log.logging.debug(f'{order_data}')
    result = {'response':
              {
                  'code': 0, 'descr': 'OK',
                  'data': {},
              },
              }
    for r in order_data['fields']:
        result['response']['data'][r] = ''
    result = dicttoxml.dicttoxml(result, root=False, attr_type=False)
    # result = xmltodict.parse(result)
    print(result)
    return result


async def change_order_state(**kwargs):
    order_id = kwargs['ORDER_ID']
    need_state = kwargs['NEED_STATE']
    result = {'response':
              {
                  'code': 0, 'descr': 'OK',
                  'data': {'order_id': order_id, 'new_state': need_state},
              },
              }
    result = dicttoxml.dicttoxml(result, root=False, attr_type=False)
    return result


async def get_order_state(**kwargs):
    order_id = kwargs['ORDER_ID']
    result = {
        "code": 0,
        "descr": "OK",
        "data": {
            "order_id": int(order_id),
            "state_id": 12,
            "state_kind": "car_at_place",
            "crew_id": 1,
            "prior_crew_id": 0,
            "driver_id": 2,
            "car_id": 3,
            "start_time": "20130117125641",
            "source_time": "20130117132617",
            "finish_time": "20130117130343",
            "source": "1",
            "destination": "2",
            "passenger": "Слепаков",
            "phone": "8800",
            "client_id": 1,
            "order_crew_group_id": 1,
            "tariff_id": 1,
            "car_mark": "Ауди",
            "car_model": "Q7",
            "car_color": "черный",
            "car_number": "А777АА",
            "confirmed": "confirmed_by_oper",
            "crew_coords": {
                "lat": 56.833981,
                "lon": 53.220249
            },
            "order_params": [
                1,
                2,
                5
            ],
            "creation_way": "operator"
        }
    }
    return result


async def set_request_state(**kwargs):
    order_data = kwargs
    order_id = order_data['ORDER_ID']
    

async def signature(data):
    # генератор подписи
    # logger.debug ('http_tmapi.signature generator')
    return hashlib.md5((data+TMAPI['sign']).encode()).hexdigest()


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
    # 'create_driver_operation': ('POST', 'common_api', '1.0', json_request, ''),
    # 'save_client_feed_back': ('POST', 'common_api', '1.0', json_request, ''),
    # 'ping': ('GET',  'common_api', '1.0', inline_request),
    # 'get_finished_orders': ('GET', 'common_api', '1.0', inline_request),
    # 'get_drivers_info': ('GET', 'common_api', '1.0', inline_request),
    # 'get_driver_info': ('GET', 'common_api', '1.0', inline_request),
    # 'check_authorization': ('GET', 'common_api', '1.0', inline_request),
    # 'get_car_info': ('GET', 'common_api', '1.0', inline_request),
    # 'get_crew_groups_list': ('GET', 'common_api', '1.0', inline_request),
    # 'get_crews_info': ('GET', 'common_api', '1.0', inline_request),
    # 'get_tariffs_list': ('GET', 'common_api', '1.0', inline_request),
    # 'get_services_list': ('GET', 'common_api', '1.0', inline_request),
    # 'get_discounts_list': ('GET', 'common_api', '1.0', inline_request),
    # 'change_order_state': ('POST', 'common_api', '1.0', inline_request),
    # 'create_order2': ('POST', 'common_api', '1.0', json_request),
    # 'get_current_orders': ('GET', 'common_api', '1.0', inline_request),
    'get_info_by_order_id': get_info_by_order_id,  # ('GET', 'tm_tapi', '1.0', inline_request),
    'change_order_state': change_order_state,
    'get_order_state': get_order_state,
    'set_request_state': set_request_state,
}
