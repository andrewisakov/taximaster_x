#!/usr/bin/python3
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
        if term_account not in term_accounts:
            with open(f'{settings.SQL_DIR}/driver_terminal_accounts.sql', 'r') as sql:
                SQL = ''.join(sql.readlines())
            with (await db_semaphore), fdb.connect(**settings.FDB) as db:
                with db.cursor as c:
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
            with db.cursor as c:
                c.execute(SQL, (term_id, ))
                try:
                    pay_term_id = c.fetchone()
                except:
                    pay_term_id = None
    return pay_term_id


async def get_pay_system(term_prefix):
    with (await pay_systems_semaphore):
        if term_prefix not in pay_systems:
            with open(f'{settings.SQL_DIR}/pay_systems.sql', 'r') as sql:
                SQL = ''.join(sql.readlines())
            with (await db_semaphore), fdb.connect(**settings.FDB) as db:
                with db.cursor as c:
                    c.execute(SQL)
                    pay_systems = {ps: int(i) for i, ps in c.fetchall()} # {'term_prefix': pay_system_id, }
        try:
            pay_system_id = pay_systems[term_prefix]
        except:
            pay_system_id = None
    return pay_system_id


async def update_driver_terminal_oper(term_id, term_opertime, term_pay_system_id, term_summ, comment):
    UPDATE = 'update driver_oper set term_operation=1, term_id=%s, term_opertime=\'%s\'' % (
            term_id, oper_data['DATE'])
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


colors = {'acquire': asyncio.BoundedSemaphore(1), }
marks = {'acquire': asyncio.BoundedSemaphore(1), }
models = {'acquire': asyncio.BoundedSemaphore(1), }
order_states = {'acquire': asyncio.BoundedSemaphore(1), }
greetings = {'acquire': asyncio.BoundedSemaphore(1), }  # {'order_state': ''}


async def get_sounds(SQL):
    with (await db_semaphore), fdb.connect(**settings.FDB) as db:
        with db.cursor() as c:
            try:
                c.execute(SQL)
                data = {k.upper(): v for k, v in c.fetchall()}
                return data
            except Exception as e:
                logger.error(e)
                db.rollback()
                return {}


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
                return greetings[order_state]
            except Exception as e:
                logger.error(e)
                return ''


def get_model(car_mark, car_model):
    car_mark = car_mark.upper().strip()
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
    car_mark = car_mark.upper()
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


def get_gosnumber(gosnumber):
    gn = []
    if len(gosnumber) == 3:
        gn.append(f'tm{gosnumber[0]}00' if gosnumber[0] != '0' else 'tm0')
        if gosnumber[1] == '1':  # 10..19
            gn.append(f'tm{gosnumber[1:]}')
        elif gosnumber[1] == '0':  # <10
            gn.append(f'tm{gosnumber[2]}' if gosnumber[0] != '0' else f'tm0&tm{gosnumber[2]}')
        else:
            gn.append(f'tm{gosnumber[1]}0')
            gn.append(f'tm{gosnumber[2]}' if gosnumber[2] != '0' else '')
    elif len(gosnumber) == 4:  # Ходят слухи... :)
        gosnumber = gosnumber[:2], gosnumber[2:]
        for g in gosnumber:
            if g[0] == '1':  # 10..19
                gn.append(f'tm{g}')
            elif g[0] == '0':
                gn.append(f'tm0')
                gn.append(f'tm{g[1]}')
            else:
                gn.append(f'tm{g[0]}0')
                if g[1] != '0':
                    gn.append(f'tm{g[1]}')
    else:
        return ''
    return '&'.join(gosnumber)
