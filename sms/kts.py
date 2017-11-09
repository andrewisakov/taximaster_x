#!/usr/bin/python3


def request_channel(address, cmd, login='user', passwd='user', realm='kts_voip', data=None):
    #print ('request_channel: %s %s %s %s %s %s' % (address, cmd, login, passwd, realm, data))
    if data:
        data = urllib.parse.urlencode(data)
        data = data.encode('utf-8')
    #address, proto = address.split(':')
    url = 'http://%s/%s' % (address, cmd)
    #print (address, url)
    auth_handler = urllib.request.HTTPDigestAuthHandler()
    auth_handler.add_password(realm=realm,
                              uri=url,
                              user=login,
                              passwd=passwd)
    opener = urllib.request.build_opener(auth_handler)
    urllib.request.install_opener(opener)
    r = urllib.request.Request(url)
    try:
        o = urllib.request.urlopen(r, data, timeout=10)
        __result = o.read().decode('UTF-8')
        __result = urllib.parse.unquote(__result)
        #logging.info('%s: Опрос %s - успешно' % (datetime.datetime.now(), address))
    except Exception as e:
        __result = "{'message': 'error', 'error': '%s'}" % e
        #.replace('<', '').replace('>', '')
        print ('request_channel: exception %s' % e)
        #logging.error('%s: Опрос %s - %s' % (datetime.datetime.now(), address, e))
        #print ('%s: Опрос %s - %s'  % (datetime.datetime.now(), address, e))
    #print ('kts.request_channel (%s/%s): %s' % (address, cmd, type(__result)))
    return __result
