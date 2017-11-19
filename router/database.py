#!/usr/bin/python3
import tornado.log
from tornado import gen

import psycopg2
from settings import PG_DSN


@gen.coroutine
def load_devices():
    # tornado.log.logging.info('load_devices')
    devices = []
    SELECT = ('select d.id as device_id, d.name as device_name, '
              'd.address as device_address, d.max_channels, '
              'c.port as channel_port, c.is_active, c.id as channel_id, '
              'sc.phone, o.name as operator_name '
              'from devices d '
              'join channels c on (c.device_id = d.id) '
              'left join sim_cards sc on (sc.id = c.sim_id) '
              'left join operators o on (o.id = sc.operator_id) '
              'order by d.address, c.port')
    con = psycopg2.connect(PG_DSN)
    tornado.log.logging.info(con)
    c = con.cursor()
    c.execute(SELECT)
    last_device_id = -1
    for d in c.fetchall():
        tornado.log.logging.info(d)
        if d[0] != last_device_id:
            device = {'id': d[0],
                      'name': d[1],
                      'address': d[2],
                      'max_channels': d[3],
                      'channels': []}
            last_device_id = d[0]
            devices.append(device)
        channel = {'port': int(f'{d[4]}'[-1]),
                   'active': d[5],
                   'id': d[6],
                   'phone': d[7],
                   'operator': d[8], }
        device['channels'].append(channel)

    return devices
