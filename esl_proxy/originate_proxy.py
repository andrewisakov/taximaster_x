#!/usr/bin/python2
# -*- coding: utf-8 -*-
import daemon
import daemon.pidfile
from daemon import runner
import asyncore
import json
import ESL
import sys
import os
import uuid
import socket
import pickle
import datetime
import settings
from settings import logger


def originate(order_data):
    with ESL.ESLConnection(*settings.ESLLogin) as e:
        if e.connected():
            uuid = e.api("create_uuid").getBody()
            logger.debug('orgiginate uuid %s' % uuid)
            originate_pickle = '/tmp/%s' % uuid
            esl_command = "expand originate"
            phones = order_data['phones']
            distributors = order_data['distributors']
            esl_data = "{origination_uuid=%s,originate_timeout=%s,ignore_early_media=true}sofia/gateway/${distributor(%s)}/%s" % (uuid, timeout, distributors[0], phones[0])
            if (len(phones) == 2) and (len(distributors) == 2):
                """Bridge driver and client"""
                esl_data = ' '.join([esl_data, "sofia/gateway/${distributor(%s)}/%s" % (distributors[1], phones[1])])
            else:
                """Callback to client"""
                with open(originate_pickle, 'wb') as fd:
                    pickle.dump(obj=order_data, file=fd, protocol=2)
                    os.fchown(fd, *settings.VOIP_USER)
                esl_data = ' '.join([esl_data, settings.SIMPLE_CALLBACK])
            logger.debug('esl_data: %s' % esl_data)
            res = e.api(esl_command, esl_data.encode('UTF-8'))
            order_data[u'uuid'] = uuid
            order_data[u'result'] = json.loads(res.serialize('json'))['_body'].replace('\n', '')
        else:
            logger.error('do not connect to ')
    return order_data


class OriginateHandler(asyncore.dispatcher_with_send):
    def handle_read(self):
        data = self.recv(8192)
        if data:
            order_data = pickle.loads(data)  # Нежелание заморачиваться с datetime in json
            originate_result = originate(order_data)
            data = pickle.dumps(originate_result, protocol=2)
            self.send(data)


class OriginateProxy(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(settings.MAX_CALLBACKS)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            logger.debug('incoming connection from {}'.format(pair))
            handler = OriginateHandler(sock)


with daemon.DaemonContext(
    working_directory=settings.APP_DIR,
    umask=0o002,
    files_preserve=[logger.handlers[0].stream.fileno(), ],
    pidfile=daemon.pidfile.PIDLockFile(settings.PID),
):
    server = OriginateProxy(**settings.ESL_PROXY)
    asyncore.loop()
