#!/usr/bin/python3
from asyncio import BundleSemaphore
import tmtapi.settings as settings
from tmtapi.settings import logger
import tmtapi.tmtapi as tmtapi
import tmtapi.database as database
import tmtapi.tmtapi as tmtapi


async def driver_term_oper_create(event, oper_data, ws, loop):
    events = []
    term_oper = await database.select_pay_term_id(oper_data['txn_id'])
    if term_oper:
        oper_id, oper_time, driver_id = term_oper
        oper_data.update(oper_id=oper_id)
        oper_data.update(oper_time=oper_time)
        oper_data.update(driver_id=driver_id)
        await ws.send_json({'DRIVER_TERM_OPER_DUBLICATE': oper_data, })
        logger.info(f'{oper_data} существует')
    else:
        driver_id = await database.get_driver_id(oper_data['account'])
        if driver_id < 0:
            logger.info(f"Недопустимый аккаунт {oper_data['account']}")
            driver_id = await database.get_driver_id(settings.FAKE_TERM_ACCOUNT)
        oper_data['driver_id'] = driver_id
        amount = oper_data['amount']
        # oper_data['oper_type'] = ['receipt', 'expense'][oper_data['oper_type']] # Приход/Расход
        request = ('create_driver_operation', {'driver_id': driver_id, 'oper_sum': amount,
                                               'oper_type': ['receipt', 'expense'][oper_data['oper_type']]})
        name = oper_data.get('name')
        comment = oper_data.get('comment')
        if name is not None:
            request[1].update(name=name)
        if comment is not None:
            request[1].update(comment=comment)
        api_result = await tmtapi.api_request(request)
        oper_id = api_result['data']['oper_id'] if api_result['code'] == 0 else 0
        if oper_id > 0:
            # Операция создана
            await ws.send_json({'DRIVER_TERM_OPER_CREATED': oper_data, })

    return event, events, oper_data


async def driver_term_oper_update(event, oper_data, ws, loop):
    events = []
    if oper_data['oper_id']
        oper_data['oper_id'] = oper_id
        oper_data['tm_oper_time'] = datetime.datetime.now()
        term_id = oper_data['txn_id']
        trm_id = oper_data['trm_id']
        pay_system_id = await database.get_pay_system_id(trm_id)
        from_amount = oper_data['from_amount']
        await database.update_driver_terminal_oper(term_id=term_id,
                                                    term_opertime=oper_data['DATA'],
                                                    term_pay_system_id=await database.get_pay_system_id(trm_id),
                                                    term_summ=oper_data['from_amount'],
                                                    comment=term_id)
        await ws.send_json({'DRIVER_TERM_OPER_UPDATED': oper_data, })
    return event, events, oper_data
