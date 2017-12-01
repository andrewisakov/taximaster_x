#!/usr/bin/python3
import datetime
import asyncio
import aiopg
from settings import logger
import settings


distributors = {}  # {'name': BoundedSemaphore()}
distributors_semaphore = asyncio.BoundedSemaphore()
distributors_cache = {}  # {('999', range_a, range_b): distributor_name, }
distributors_cache_semaphore = asyncio.BoundedSemaphore()
smsc_cache = {}  # {}


async def select_distributor(phone, pool):
    """Выборка дистрибьютора из БД"""
    phone = phone[-10:]
    phone = (settings.LOCAL_CODE + phone) if len(phone) < max(settings.PHONE_LENGTH) else phone
    ARGS = (phone[:3], int(phone[3:]))
    with (await distributors_semaphore):  # Лочка на случай, если в базу лезть придётся
        distributor = tuple(d[1] for d in tuple(filter(lambda x:
                                                       (x[0][0] == ARGS[0]) and
                                                       (x[0][1] <= ARGS[1]
                                                        <= x[0][2]),
                                                       distributors_cache.items())))
        if not distributor:  # Не нашли в кэше
            logger.info(f'Отсутствует {phone} в кэше.')
            with open(f'{settings.SQL_DIR}/select_distributor.sql', 'r') as sql:
                SQL = ''.join(sql.readlines())
            # async with aiopg.create_pool(dsn=settings.PG_DSN) as pool:
            async with (await pool.acquire()) as db:
                async with (await db.cursor()) as c:
                    await c.execute(SQL, ARGS)
                    try:
                        distributor, cut_code, distributor_id, a, b = await c.fetchone()
                        distributors_cache.update(
                            {(ARGS[0], a, b): (distributor, cut_code, distributor_id)})
                    except Exception as e:
                        logger.info(e)
                        distributor, cut_code, distributor_id = 'inter_city', None, 0
        else:
            logger.info(f'{distributor} {phone} найден в кэше.')
            distributor, cut_code, distributor_id = distributor[0]

    async with distributors_cache_semaphore:  # Лочка на судчай в базу лезть
        if distributor not in distributors.keys():  # На нашли в кэше
            logger.info(f'Отсутствует семафор для {distributor}')
            with open(f'{settings.SQL_DIR}/distributors.sql') as sql:
                SQL = ''.join(sql.readlines())
            async with (await pool.acquire()) as db:
                async with (await db.cursor()) as c:
                    await c.execute(SQL)
                    async for d in c:
                        if d[0] not in distributors.keys():
                            distributors[d[0]] = asyncio.BoundedSemaphore(d[1])
                        else:
                            distributors[d[0]]._value = d[1]

    phone = (settings.REGIO_CODE + phone)  # Привести номер телефога к окончательному виду
    return distributor, phone


async def select_smsc(phone, pool):
    """Выбока SMS шлюза из БД"""
    phone = phone[-10:]
    phone = (settings.LOCAL_CODE + phone) if len(phone) < max(settings.PHONE_LENGTH) else phone
    ARGS = (datetime.datetime.now()-datetime.timedelta(days=1), phone[:3], int(phone[3:]), )
    logger.info(f'smsc {ARGS}')
    smsc, channel, sended = None, None, None
    with open(f'{settings.SQL_DIR}/select_smsc.sql', 'r') as sql:
        SQL = ''.join(sql.readlines())
    async with (await pool.acquire()) as db:
        async with (await db.cursor()) as c:
            await c.execute(SQL, ARGS)
            smsc = await c.fetchone()
            smsc, channel, sended = smsc[1], smsc[2] % 5060, smsc[3]
    phone = (settings.REGIO_CODE + phone)
    return smsc, channel, sended, phone
