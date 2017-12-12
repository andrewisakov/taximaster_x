#!/usr/bin/python3
import sys
import traceback2
import fdb
import datetime
from asyncio import BoundedSemaphore
import tmtapi.settings as settings
from tmtapi.settings import logger


# db = fdb.connect(**settings.FDB)
db_semaphore = BoundedSemaphore(settings.FDB_PARALLEL_OPERS)
term_accounts_semaphore = BoundedSemaphore()
term_accounts = {}
pay_systems_semaphore = BoundedSemaphore()
pay_systems = {}


async def get_driver_id(term_account):
    with (await term_accounts_semaphore):
        global term_accounts
        if term_account not in term_accounts:
            with open(f'{settings.SQL_DIR}/driver_terminal_accounts.sql', 'r') as sql:
                SQL = ''.join(sql.readlines())
            with (await db_semaphore), fdb.connect(**settings.FDB) as db:
                with db.cursor() as c:
                    c.execute(SQL)
                    term_accounts = {k: int(v) for k, v in c.fetchall()}
        try:
            driver_id = term_accounts[term_account]
        except:
            driver_id = -1
    return driver_id


async def select_pay_term_id(term_id):
    with (await db_semaphore):
        with open(f'{settings.SQL_DIR}/select_pay_term_id.sql') as sql:
            SQL = ''.join(sql.readlines())
        with (await db_semaphore), fdb.connect(**settings.FDB) as db:
            with db.cursor() as c:
                c.execute(SQL, (term_id, ))
                try:
                    pay_term_id = c.fetchone()
                except:
                    pay_term_id = None
    return pay_term_id


async def get_pay_system(term_prefix):
    with (await pay_systems_semaphore):
        global pay_systems
        if term_prefix not in pay_systems:
            with open(f'{settings.SQL_DIR}/pay_systems.sql', 'r') as sql:
                SQL = ''.join(sql.readlines())
            with (await db_semaphore), fdb.connect(**settings.FDB) as db:
                with db.cursor() as c:
                    c.execute(SQL)
                    pay_systems = {ps: int(i) for i, ps in c.fetchall()}  # {'term_prefix': pay_system_id, }
        try:
            pay_system_id = pay_systems[term_prefix]
        except:
            pay_system_id = None
    return pay_system_id


async def update_driver_terminal_oper(term_id, term_opertime, term_pay_system_id, term_summ, comment, oper_id):
    UPDATE = 'update driver_oper set term_operation=1, term_id=%s, term_opertime=\'%s\'' % (
        term_id, term_opertime)
    if term_pay_system_id:
        # id платёжной системы
        UPDATE += ', term_pay_system_id=%s' % term_pay_system_id
    if term_summ:
        # Внесённая сумма
        UPDATE += ', term_summ=%s' % term_summ
    if comment:
        UPDATE += ', comment=\'%s\'' % comment
    UPDATE += ' where id=%s' % oper_id
    with (await db_semaphore), fdb.connect(**settings.FDB) as db:
        try:
            with db.cursor() as c:
                c.execute(UPDATE)
            db.commit()
            logger.info(f'driver_opers.id={oper_id} updated')
            updated = True
        except Exception as e:
            db.rollback()
            logger.info(f'driver_opers.id={oper_id} updating error {e}')
            updated = True
    return updated


colors = {'acquire': BoundedSemaphore(1), }
marks = {'acquire': BoundedSemaphore(1), }
models = {'acquire': BoundedSemaphore(1), }
order_states = {'acquire': BoundedSemaphore(1), }
greetings = {'acquire': BoundedSemaphore(1), }  # {'order_state': ''}


async def get_sounds(SQL):
    with (await db_semaphore), fdb.connect(**settings.FDB) as db:
        c = db.cursor()
        try:
            c.execute(SQL)
            data = {k.upper(): f'{v}' for k, v in c.fetchall()}
            # logger.info(f'{data}')
        except Exception as e:
            logger.error(e)
            db.rollback()
            data = {}
        c.close()
    return data


async def get_greeting(order_state):
    order_state = order_state.upper()
    with (await greetings['acquire']):
        if order_state in greetings.keys():
            return greetings[order_state]
        else:
            try:
                data = await get_sounds('select name, description from asterisk_sounds where (sound_type=4) and (description is not null)')
                # data = {k.upper(): v for k, v in data.items()}
                logger.info(f'get_greeting: {data}')
                greetings.update(data)
                logger.info(f'{greetings[order_state]}')
                return greetings[order_state]
            except Exception as e:
                logger.error(e)
                logger.error(traceback2.extract_tb(sys.exc_info()[2]))
                return ''


async def get_model(car_mark, car_model):
    car_mark = car_mark.upper().strip().split(' ')[0]
    if car_mark == 'ВАЗ':
        if car_model in models.keys():
            return models[car_model]
        else:
            ma = []
            mo = []
            ma.append(car_model[:2])
            if len(car_model) == 5:
                ma.append(car_model[2])
            ma.append(car_model[-2:])
            for m in ma:
                if len(m) == 2:
                    if m[0] == '1':
                        mo.append(f'tm{m}')
                    elif m[0] == '0':
                        mo.append(f'tm0&tm{m[1]}')
                    else:
                        mo.append(f'tm{m[0]}0&tm{m[1]}')
                else:
                    mo.append(f'tm{m}')
            mo = '&'.join(mo)
            models.update({car_model: mo})
            return mo
    else:
        return ''


async def get_mark(car_mark):
    car_mark = car_mark.upper().strip().split(' ')[0]
    with (await marks['acquire']):
        if car_mark in marks.keys():
            return marks[car_mark]
        else:
            try:
                data = await get_sounds('select name, sound_file from asterisk_sounds where (sound_type=0) and (sound_file is not null)')
                # data = {k.upper(): v for k, v in data}
                marks.update(data)
                return marks[car_mark]
            except Exception as e:
                logger.error(e)
                return ''


async def get_color(car_color):
    car_color = car_color.upper()
    with (await colors['acquire']):
        if car_color in colors.keys():
            return colors[car_color]
        else:
            try:
                data = await get_sounds('select name, sound_file from asterisk_sounds where (sound_type=1) and (sound_file is not null)')
                colors.update(data)
                return colors[car_color]
            except Exception as e:
                logger.error(e)
                return ''


async def get_gosnumber(gosnumber):
    gn = []
    if len(gosnumber) == 3:
        gn.append(f'ru/tm{gosnumber[0]}00' if gosnumber[0] != '0' else 'ru/tm0')
        if gosnumber[1] == '1':  # 10..19
            gn.append(f'tm{gosnumber[1:]}')
        elif gosnumber[1] == '0':  # <10
            gn.append(f'tm{gosnumber[2]}' if gosnumber[0] != '0' else f'ru/tm0&ru/tm{gosnumber[2]}')
        else:
            gn.append(f'tm{gosnumber[1]}0')
            gn.append(f'tm{gosnumber[2]}' if gosnumber[2] != '0' else '')
    elif len(gosnumber) == 4:  # Ходят слухи... :)
        gosnumber = gosnumber[:2], gosnumber[2:]
        for g in gosnumber:
            if g[0] == '1':  # 10..19
                gn.append(f'ru/tm{g}')
            elif g[0] == '0':
                gn.append(f'ru/tm0')
                gn.append(f'ru/tm{g[1]}')
            else:
                gn.append(f'ru/tm{g[0]}0')
                if g[1] != '0':
                    gn.append(f'ru/tm{g[1]}')
    else:
        return ''
    return '&'.join(gn)


async def get_minutes(driver_timecount):
    # minutes = int(minutes)
    if driver_timecount > 0:
        if driver_timecount > 19:
            minutes = (driver_timecount // 10, driver_timecount % 10)
            minutes = f'ru/tm{minutes[0]}0&ru/tm{minutes[1]}&'
        else:
            minutes = f'ru/tm{driver_timecount}&'
    else:
        minutes = 'ru/tm5&ru/tm7&'
    return minutes


async def get_voip_message(order_data):
    logger.info(f'get_voip_message: {order_data}')
    order_state = order_data['state'].upper()
    voip_message = await get_greeting(order_state)
    if voip_message:
        if order_state != 'NO_CARS':
            mark = await get_mark(order_data['car_mark'])
            logger.info(f'get_voip_message: {mark}')
            voip_message = voip_message.replace('$mark', mark if mark else '')
            model = await get_model(order_data['car_mark'], order_data['car_model'])
            logger.info(f'get_voip_message: {model}')
            voip_message = voip_message.replace('$model', model if model else '')
            color = await get_color(order_data['car_color'])
            logger.info(f'get_voip_message: {color}')
            voip_message = voip_message.replace('$color', color)
            if not color:
                voip_message = voip_message.replace('&ru/tmColor&', '')
            gosnumber = await get_gosnumber(order_data['gosnumber'])
            logger.info(f'get_voip_message: {gosnumber}')
            if not gosnumber:
                voip_message = voip_message.replace('&ru/tmgosnomer&', '')
            voip_message = voip_message.replace('$gosnumber', gosnumber)
            minutes = await get_minutes(order_data['driver_timecount'])
            voip_message = voip_message.replace('$minutes', minutes)
    voip_message = [f'{vm}.wav' for vm in voip_message.split('&') if vm]
    logger.info(f'get_voip_message: {voip_message}')
    return voip_message


async def get_sms_message(order_data):
    sms_message = order_data['car_mark']
    sms_message += (' ' + order_data['car_model'] + '\n') if order_data['car_model'] else '\n'
    sms_message += (order_data['car_color'] + '\n') if order_data['car_color'] else ''
    if order_data['driver_timecount'] > 0:
        sms_message += f"{order_data['driver_timecount']}"
    else:
        sms_message += '5-7'
    sms_message += 'мин\n'
    sms_message += settings.SMS_SIGN
    return sms_message
