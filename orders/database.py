#!/usr/bin/python3
import fdb
import asyncio
import orders.settings as settings
from orders.settings import logger


colors = {'acquire': asyncio.BoundedSemaphore(1),}
marks = {'acquire': asyncio.BoundedSemaphore(1),}
models = {'acquire': asyncio.BoundedSemaphore(1),}
order_states = {'acquire': asyncio.BoundedSemaphore(1),}
greetings = {'acquire': asyncio.BoundedSemaphore(1),}  # {'order_state': ''}


conn = fdb.connect(**settings.FDB)


@asyncio.coroutine
def get_sounds(SQL):
    try:
        c = conn.cursor()
        c.execute(SQL)
        data = {k.upper(): v for k, v in c.fetchall()}
        c.close()
        yield data
    except Exception as e:
        logger.error(e)
        db.rollback()
        yield {}


@asyncio.coroutine
def get_greeting(order_state):
    order_state = order_state.upper()
    with greetings['acquire']:
        if order_state in greetings.keys():
            yield greetings[order_state]
        else:
            try:
                data = yield from get_query('select name, description from asterisk_sounds where (sound_type=4) and (description is not null)')
                greetings.update(data)
                yield greetings[order_state]
            except Exception as e:
                logger.error(e)
                yield ''


@asyncio.coroutine
def get_model(car_mark, car_model):
    car_mark = car_mark.upper().strip()
    if car_mark == 'ВАЗ':
        if car_model in models.keys():
            yield models[car_model]
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
            models[car_model] = mo
            yield mo
    else:
        yield ''



@asyncio.coroutine
def get_mark(car_mark):
    car_marks = car_marks.upper()
    with marks['acquire']:
        if car_mark in marks.keys():
            yield marks[car_mark]
        else:
            try:
                data = yield from get_query('select name, sound_file from asterisk_sounds where (sound_type=0) and (sound_file is not null)')
                marks.update(data)
                yield marks[car_mark]
            except Exception as e:
                logger.error(e)
                yield ''


@asyncio.coroutine
def get_color(car_color):
    car_color = car_color.upper()
    with colors['acquire']:
        if car_color in colors.keys():
            yield colors[car_color]
        else:
            try:
                data = yield from get_query('select name, sound_file from asterisk_sounds where (sound_type=1) and (sound_file is not null)')
                colors.update(data)
                yield colors[car_color]
            except Exception as e:
                logger.error(e)
                yield ''


@asyncio.coroutine
def get_gosnumber(gosnumber):
    gn = []
    if len(gosnumber) == 3:
        gn.append(f'tm{gosnumber[0]}00' if gosnumber[0] != '0' else 'tm0')
        if gosnumber[1] == '1':  # 10..19
            gn.append(f'tm{gosnumber[1:]}')
        elif gosnumber[1] == '0': # <10
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
        yield ''
    yield '&'.join(gosnumber)
