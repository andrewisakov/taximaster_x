#!/usr/bin/python3
import tornado.log
from tornado import gen
import hashlib
import dicttoxml
import xmltodict
from settings import TMAPI


ORDER_STATES = {
    'order_created': ('Создан', 1, ),
    'order_aborted': ('Прекращён', 5, ),
    'order_completed': ('Выполнен', 4, ),
    'order_client_in_car': ('Клиент в машине', 11, ),
    'order_client_gone': ('Клиент не выходит', 23, ),
    'order_client_fuck': ('Клиент не вышел', 12, ),
    'order_crew_at_place': ('Экипаж на месте', 10),
    'order_no_cars': ('Нет машин', 68, ),
    'order_no_cars_aborted': ('Нет машин: Преращён', 6, ),
    'order_accepted': ('Водитель принял заказ', 7, ),
    'order_denied_driver': ('Водитель отказался от заказа', 9, ),
    }
ORDERS = [{'id': 18561, 'state': 0, 'starttime': '', 'finishtime': '',
           'discountedsumm': 70.0, 'phone_to_callback': '89278831370',
           'crew_id': 0, 'callback_state': 0, 'creation_way': 'operator',
           'sourcetime': '', 'source': '', 'destination': '',
           'client_id': 1, 'driver_timecount': 0, 'state_id': 1,
           'call_back_to_client_state': 0, }, ]
ORDER_H = {}
CLIENTS = [{'id': 1, 'card_no': '0337', 'name': 'Андрей', }]
CREWS = [{'id': 1, 'car_id': 1, 'driver_id': 1}, ]
CARS = [{'id': 1, 'color': 'красный', 'mark': 'ВАЗ', 'model': '2114',
         'gosnumber': '515'}, ]

DRIVERS = [{'id': 1, 'term_account': '01181', 'phone': '88001001010', }, ]
CALLBACK_STATES = ('order_callback_accepted', 'order_callback_started',
                   'order_callback_delivered', 'order_callback_busy',
                   'order_callback_no_answer', 'order_callback_error')

async def get_info_by_order_id(order_data):
    # order_data = kwargs
    tornado.log.logging.info(f'{order_data}')
    if 'fields' in order_data.keys():
        order_data['fields'] = tuple([f for f in order_data['fields'].split('-')])
    order_id = order_data['order_id']
    result = {'response':
              {
                  'code': 0, 'descr': 'OK',
                  'data': {},
              },
              }
    for r in order_data['fields']:
        result['response']['data'][r] = ''

    dicttoxml.set_debug(False)
    result = dicttoxml.dicttoxml(result, root=False, attr_type=False)
    # result = xmltodict.parse(result)
    tornado.log.logging.info(result)
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
    dicttoxml.set_debug(False)
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
    order = tuple(filter(lambda x: x['id'] == order_id, ORDERS))
    order = order[0] if order else []
    if order:
        order[0]['call_back_to_client_state'] = order_data['state']
        return '<response><code>0</code><descr>OK</descr></response>'
    else:
        return '<response><code>100</code><descr>ERROR</descr></response>'


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
