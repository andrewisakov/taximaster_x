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


def originate(originate_data):
    # logger.debug('originate: {}'.format(originate_data))
    e = ESL.ESLconnection(*settings.ESLLogin)
    logger.debug('originate: {}'.format(e))
    if e.connected():
        uuid = e.api("create_uuid").getBody()
        logger.debug('originate uuid %s' % uuid)
        esl_command = "expand originate"
        phones = originate_data['phones']
        distributors = originate_data['distributors']
        # logger.debug('orgiginate {} {}'.format(phones, distributors))
        esl_data = "{origination_uuid=%s,originate_timeout=%s,ignore_early_media=true}sofia/gateway/${distributor(%s)}/%s" % (
            uuid, settings.ESL_TIMEOUT, distributors[0], phones[0])
        logger.debug('originate {} {}'.format(esl_command, esl_data))
        if (len(phones) == 2) and (len(distributors) == 2):
            """Bridge driver and client"""
            esl_data = ' '.join(
                [esl_data, "sofia/gateway/${distributor(%s)}/%s" % (distributors[1], phones[1])])
        else:
            """Callback to client"""
            originate_pickle = '/tmp/%s' % uuid
            with open(originate_pickle, 'wb') as fd:
                pickle.dump(obj=originate_data, file=fd, protocol=2)
            os.chown(originate_pickle, *settings.VOIP_USER)
            esl_data = ' '.join([esl_data, settings.SIMPLE_CALLBACK])
        logger.debug('originate: {} {}'.format(esl_command, esl_data))
        res = e.api(esl_command, esl_data.encode('UTF-8'))
        logger.debug('originate: {}'.format(json.loads(res.serialize('json'))['_body'].replace('\n', '')))
        originate_data[u'uuid'] = uuid
        originate_data[u'result'] = json.loads(res.serialize('json'))['_body'].replace('\n', '')
        e.disconnect()
    else:
        logger.error('do not connect to ')
    return originate_data


class OriginateHandler(asyncore.dispatcher_with_send):
    def handle_read(self):
        data = self.recv(8192)
        if data:
            bridge_data = pickle.loads(data)  # Нежелание заморачиваться с datetime in json
            logger.debug('OriginateHandler: {}'.format(bridge_data))
            originate_result = originate(bridge_data)
            logger.debug('OriginateHandler: {}'.format(originate_result))
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
