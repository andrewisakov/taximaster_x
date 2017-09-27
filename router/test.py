#!/usr/bin/python3
import json
import urllib
import urllib.request
import hashlib
import ssl
import xmltodict
import datetime
import logging
from settings import PORT as port
import tmtapi


def request(url, params, method='GET'):
    req = urllib.request.Request(url, method=method)
    # for header in headers:
    #     req.add_header(header, headers[header])
    # context = ssl._create_unverified_context()
    r = urllib.request.urlopen(req, params.encode() if method == 'POST'\
                               else None).read()
    return r

url = f'http://127.0.0.1:{port}/'
data = dict(name='order_accepted',
            startparam1='9278831370',
            startparam3=1,
            atartparam4=1000001)


params = urllib.parse.urlencode(data)
url += params
params = None
response = request(url, params)
print(response)
