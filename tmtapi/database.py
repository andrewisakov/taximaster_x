#!/usr/bin/python3
import fdb
import datetime
from asyncio import BoundedSemaphore
import tmtapi.settings as settings
from tmtapi.settings import logger


db = fdb.connect(**settings.FDB)
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
            with fdb.connect(**settings.FDB) as db:
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
        with fdb.connect(**settings.FDB) as db:
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
            with fdb.connect(**settings.FDB) as db:
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
    with (await db_semaphore):
        with fdb.connect(**settings.FDB) as db:
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
