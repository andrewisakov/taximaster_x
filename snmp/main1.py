#!/usr/bin/python3
from textwrap import wrap
import datetime
import pickle
import glob
import sys
import traceback
import binascii


pack = b'0\x82\x01\x9c\x02\x01\x01\x04\x07ktsvoip\xa7\x82\x01\x8c\x02\x046\xd27[\x02\x01\x00\x02\x01\x000\x82\x01|0\x10\x06\x08+\x06\x01\x02\x01\x01\x03\x00C\x04\x02O\xe4\x070\x19\x06\n+\x06\x01\x06\x03\x01\x01\x04\x01\x00\x06\x0b+\x06\x01\x04\x01\x82\xadU\n\x02\x030\x10\x06\x0b+\x06\x01\x04\x01\x82\xadU\n\x01\x03\x02\x01\x000\x81\xfe\x06\x0b+\x06\x01\x04\x01\x82\xadU\n\x01\x07\x04\x81\xee07919761980693F02410D0E7F7BC3E67D7CF690008711161906561215A041F04300440043E043B044C00200434043B044F0020043F043504400432043E0433043E002004320445043E0434043000200432002004410438044104420435043C0443003A002000350050006700650043007700510066002E0(\x06\x0b+\x06\x01\x04\x01\x82\xadU\n\x01\x0b\x04\x19SMS incomming event alarm0\x10\x06\x0b+\x06\x01\x04\x01\x82\xadU\n\x01\x01\x02\x01\x03'

GSM_REG_FLAG = (0xf1, 0xf0, 0xf3)
GSM_SMS_FLAG = (0xec, 0xeb, )
SIP_PROGRESS = (0x01, )


EVENTS = {
    GSM_REG_FLAG[0]: {1: ('channel', int),
                      3: ('state_id', int),
                    #   7: ('reg', str),
                      8: ('LAC', str),
                      9: ('cell', str),
                      11: ('event', str),
                      'events': {0: 'GSM_UNREGISTERED', 1: 'GSM_REGISTERED_HOME', 2: 'GSM_SEARCH', 3: 'GSM_REGITRATION_LOCKED', 4: 'GSM_REGISTERED_UNKNOWN', 5: 'GSM_REGISTERED_ROAMING'},
                      },
    GSM_SMS_FLAG[0]: {1: ('channel', int),
                      3: ('state_id', int),
                      7: ('pdu', dict),  # {sca, da, udl, pid, ud}
                      11: ('event', str),
                      'events': {0: 'SMS_INCOMING', 1: 'SMS_BROADCAST', 2: 'SMS_DELIVERED', '99': 'SMS_UNCNOWN'},
                      },
    SIP_PROGRESS[0]: {1: ('channel', int),
                      3: ('state_id', int),
                      5: ('duration', int),
                      7: ('caller', str),
                      8: ('callee', str),
                      #   9: ('state', str),
                      10: ('state_descr', str),
                      11: ('event', str),
                      'events': {1: 'SIP_INCOMING', 2: 'SIP_INVITE', 3: 'SIP_EARLY', 4: 'SIP_CONNECTING', 5: 'SIP_CONFIRMED', 6: 'SIP_DISCONNCTED', },
                      },
}
EVENTS.update({GSM_SMS_FLAG[1]: EVENTS[GSM_SMS_FLAG[0]]})
EVENTS.update({GSM_REG_FLAG[2]: EVENTS[GSM_REG_FLAG[0]]})
EVENTS.update({GSM_REG_FLAG[1]: EVENTS[GSM_REG_FLAG[0]]})


def parse_pdu(pdu):
    pdu = wrap(pdu, 2)
    sca_len = eval(f'0x{pdu.pop(0)}')
    sca_type = pdu.pop(0)  # 91
    sca = pdu[:sca_len-1]
    sca = ''.join([c[::-1] for c in sca])[:11]  # Ипанаты. тут байты
    pdu = pdu[sca_len:]
    pdu_type = (eval(f'0x{pdu.pop(0)}') >> 3) & 0x03
    num_len = eval(f'0x{pdu.pop(0)}')
    pdu.pop(0)
    num = pdu[:sum(divmod(num_len, 2))]
    num = ''.join([c[::-1] for c in num][:num_len])[:num_len]  # А тут знаки
    pid = pdu.pop(0)
    dcs = pdu.pop(0)
    pdu = pdu[(0, 0, 1, 7)[pdu_type]:]  # Отхряпать datetime
    udl = eval(f'0x{pdu.pop(0)}')
    # return {'SCA': sca, 'DA': num, 'UDL': udl, 'PID': pid, 'UD': ''.join(pdu), 'DCS': dcs}
    return {'SCA': sca, 'DA': num, 'UDL': udl, 'PID': pid, }


def parse_header(pack):
    pack = wrap(pack.hex(), 2)
    print(''.join(pack))
    pos = 4
    HEADER = eval(f'0x{pack[2]}')
    if pack[0] == '30':
        if (HEADER in (0xf1, 0xec, 0xeb)):
            pos -= 1
        VER_LEN = eval(f'0x{pack[pos]}')
        pos += 1
        VER = pack[pos:pos+1]
        pos += VER_LEN
        if pack[pos] == '04':  # Точно заголовок?
            pos += 1
            PASS_LEN = eval(f'0x{pack[pos]}')
            pos += 1
            PASS = bytes.fromhex(''.join(pack[pos:pos+PASS_LEN])).decode()
            pos += PASS_LEN
            PUD = pack[pos]
            pos += 4  # неясные позиции
            if (HEADER in GSM_REG_FLAG+GSM_SMS_FLAG):
                pos -= 1
            T3 = pack[pos]
            pos += 1
            ID_LEN = eval(f'0x{pack[pos]}')
            pos += 1
            ID = ''.join(pack[pos:pos+ID_LEN])
            pos += ID_LEN
            T4 = pack[pos]
            pos += 1
            REQ_LEN = eval(f'0x{pack[pos]}')
            pos += 1
            REQ_VAL = ''.join(pack[pos:pos+REQ_LEN])
            pos += REQ_LEN
            T5 = pack[pos]
            pos += 1
            ERR_LEN = eval(f'0x{pack[pos]}')
            pos += 1
            ERR_ID = pack[pos:pos+ERR_LEN]
            pos += ERR_LEN
            pos += 4
            if (HEADER in GSM_REG_FLAG+GSM_SMS_FLAG):
                pos -= 1
            # return pack[pos:], {'HEADER': HEADER, 'PASS': PASS, 'ID': ID, 'REQ': REQ_VAL, 'PUD': PUD}
            return pack[pos:], {'HEADER': HEADER, 'ID': eval(f'0x{ID}'), }


def parse_block(pack, header):
    pos = 0
    if pack[pos] == '30':  # Флаг начала блока
        pos += 1
        BLOCK_LEN = eval(f'0x{pack[pos]}')
        pos += 1
        Ttm = pack[pos]
        pos += 1
        LEN_tm = eval(f'0x{pack[pos]}')
        pos += 1
        MIB = tuple(eval(f'0x{c}') for c in pack[pos:pos+LEN_tm])
        pos += LEN_tm
        pos += 1  # неясная позиция
        TAIL_LEN = eval(f'0x{pack[pos]}')
        pos += 1
        TAIL = pack[pos:pos+TAIL_LEN]
        pos += TAIL_LEN
        if MIB[-1] > 6:
            TAIL = bytes.fromhex(''.join(TAIL))
            print(TAIL)
            # .decode()
        else:
            TAIL = ''.join(TAIL)
        if (header in GSM_SMS_FLAG) and (MIB[-1] == 7):  # Вхоящее СМС
            TAIL = parse_pdu(TAIL)
        data = {}
        if (header in EVENTS) and (MIB[-1] in EVENTS[header]):
            if EVENTS[header][MIB[-1]][1] is int:
                TAIL = eval(f'0x{TAIL}')
            # if EVENTS[header][MIB[-1]][1] is str
            data.update({EVENTS[header][MIB[-1]][0]: TAIL})
            # data.update({'event': EVENTS[header]['events'][]})
        MIB = '.'.join([str(mib) for mib in MIB])
        # return pack[pos:], {'LEN': BLOCK_LEN, 'MIB': MIB, 'TAIL': TAIL, 'data': data}
        return pack[pos:], data


if __name__ == '__main__':

    try:
        pack, header = parse_header(pack)
        pack1 = pack
        # print(header)
        header.update({'timestamp': f'{datetime.datetime.now()}'})
        body = {}
        while pack:
            pack, block = parse_block(pack, header['HEADER'])
            # print(block)
            if block:
                body.update(block)
            # print(pack)
        body.update({'event': EVENTS[header['HEADER']]['events'][body['state_id']]})
        header.update({'address': addr})
        body.update({'header': header})
        print(body)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f'{pack1}')
        print(e)
        print(repr(traceback.extract_tb(exc_traceback)))
