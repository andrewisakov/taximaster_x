from browser import document as doc, ajax, html
import json


def send_ajax(data, url, method, on_complete):
    # print('send_ajax data:', data)
    req = ajax.ajax()
    req.bind('complete', on_complete)
    req.open(method.upper(), url, True)
    req.set_header('Content-type', 'application/json')
    req.send(json.dumps(data))


def change_order_state(ev):
    def on_complete(req):
        data = json.loads(req.text)
        print(data)
        if data['code'] == 0:
            if data['state'] == 'order_created':
                ev.target.parent.getElementsByClassName('starttime').text = data['starttime']
            if data['state'] == 'order_completed':
                ev.target.parent.getElementsByClassName('finishtime').text = data['finishtime']
        else:
            pass

    # print(dir(ev))
    send_ajax(data={'order_id': ev.target.parent.getElementsByClassName('order_id')[0].text,
                    'order_state': ev.target.parent.getElementsByClassName('order_state')[0].value,
                    'order_crew_id': ev.target.parent.getElementsByClassName('crew')[0].value,
                    'order_phone_to_callback': ev.target.parent.getElementsByClassName('phone_to_callback')[0].text,
                    'order_driver_timecount': ev.target.parent.getElementsByClassName('driver_timecount')[0].value,
                    },
              url='/change_order_state',
              method='post',
              on_complete=on_complete)

for button in doc.getElementsByClassName('change_state'):
    button.bind('click', change_order_state)

