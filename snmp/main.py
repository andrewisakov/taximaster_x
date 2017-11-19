import asyncio
import aiohttp
import datetime
import socket
import json
import settings
from settings import logger
import snmp


def send_result(future):
    logger.info('event_result: f{future.result()}')


async def send_on_router(body):
    async with aiohttp.ClientSession() as session:
        async with session.post(settings.ROUTER_URL,
                                data=body,
                                headers={'content-type': 'application/json'}) as resp:
            response = await resp.json()
            logger.info(f'{response}')
            return response


class SNMPServerProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        pack, header = snmp.parse_header(data)
        header.update({'timestamp': f'{datetime.datetime.now()}'})
        body = {}
        while pack:
            pack, block = snmp.parse_block(pack, header['HEADER'])
            # print(block)
            if block:
                body.update(block)
            # print(pack)
        body.update({'event': snmp.EVENTS[header['HEADER']]['events'][body['state_id']]})
        header.update({'address': addr[0]})
        body.update({'header': header})
        logger.info(f'{body}')
        task = loop.create_task(send_on_router(body))
        task.add_done_callback(send_result)


loop = asyncio.get_event_loop()
listen = loop.create_datagram_endpoint(
    SNMPServerProtocol, local_addr=(settings.IP, settings.PORT))
transport, protocol = loop.run_until_complete(listen)
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()
