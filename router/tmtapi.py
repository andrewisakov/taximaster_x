#!/usr/bin/python3
import asyncio


@asyncio.coroutine
def order_create(order_data):
    {'PHONE': order_data['calleeid'],
     'ORDER_STATE_ID': 1,
     'CREWGROUPID': <Группа «Рация»>,
     'TARIF_ID': <Тариф>,
     'STARTUSER': <service_name_id>,
     'PHONE_TO_DIAL': order_data['callerid'],
     'FROMBORDER': 1,
     'INPUTTIME': datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
    }

    return order_data


