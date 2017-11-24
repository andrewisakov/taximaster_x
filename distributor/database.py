#!/usr/bin/python3
import datetime
import asyncio
# from asyncio import BoundedSemaphore
# from tornado.locks import BoundedSemaphore
# import tornado.log
# import tornado.locks
import psycopg2 as pg2
from distributor.settings import logger
try:
    import settings
except:
    import distributor.settings as settings


distributors = {}  # {'name': BoundedSemaphore()}
distributors_semaphore = asyncio.BoundedSemaphore()
distributors_cache = {}  # {('999', range_a, range_b): 'distributor_name', }
distributors_cache_semaphore = asyncio.BoundedSemaphore()
smsc_cache = {}  # {}


@asyncio.coroutine
def get_smsc(phone):
    phone = phone[-10:]
    phone = (settings.LOCAL_CODE + phone) if len(phone) < max(settings.PHONE_LENGTH) else phone
    ARGS = (datetime.datetime.now()-datetime.timedelta(days=1), phone[:3], int(phone[3:]), )
    logger.info(f'smsc {ARGS}')
    smsc, channel, sended = None, None, None
    with open(f'{settings.SQL_DIR}/select_smsc.sql', 'r') as sql:
        SQL = ''.join(sql.readlines())
    with pg2.connect(dsn=settings.PG_DSN) as db:
        with db.cursor() as c:
            c.execute(SQL, ARGS)
            smsc = c.fetchone()
            smsc, channel, sended = smsc[1], smsc[2] % 5060, smsc[3]
    phone = (settings.REGIO_CODE + phone)
    return smsc, channel, sended, phone


@asyncio.coroutine
def get_distributor(phone):
    phone = phone[-10:]
    phone = (settings.LOCAL_CODE + phone) if len(phone) < max(settings.PHONE_LENGTH) else phone
    ARGS = (phone[:3], int(phone[3:]))
    with (yield from distributors_semaphore):
        distributor = tuple(d[1] for d in tuple(filter(lambda x:
                                                       (x[0][0] == ARGS[0]) and
                                                       (x[0][1] <= ARGS[1]
                                                        <= x[0][2]),
                                                       distributors_cache.items())))
        if not distributor:
            logger.info(f'Отсутствует {distributor} в кэше.')
            with open(f'{settings.SQL_DIR}/select_distributor.sql', 'r') as sql:
                SQL = ''.join(sql.readlines())
            with pg2.connect(dsn=settings.PG_DSN) as db:
                with db.cursor() as c:
                    c.execute(SQL, ARGS)
                    try:
                        distributor, cut_code, distributor_id, a, b = c.fetchone()
                        distributors_cache.update(
                            {(ARGS[0], a, b): (distributor, cut_code, distributor_id)})
                    except Exception as e:
                        tornado.log.logging.info(e)
                        distributor, cut_code, distributor_id = 'inter_city', None, 0
        else:
            logger.info(f'{distributor} найден в кэше.')
            distributor, cut_code, distributor_id = distributor[0]

    with (yield from distributors_cache_semaphore):
        if distributor not in distributors.keys():
            logger.info(f'Отсутствует семафор {distributor}')
            with open(f'{settings.SQL_DIR}/distributors.sql') as sql:
                SQL = ''.join(sql.readlines())
            with pg2.connect(dsn=settings.PG_DSN) as db:
                with db.cursor() as c:
                    c.execute(SQL)
                    for d in c.fetchall():
                        if d[0] not in distributors.keys():
                            distributors[d[0]] = asyncio.BoundedSemaphore(d[1])
                        else:
                            distributors[d[0]]._value = d[1]

    # logger.info(f'{distributors}')
    # logger.info(f'{distributors_cache}')
    phone = (settings.REGIO_CODE + phone)
    return distributor, phone
