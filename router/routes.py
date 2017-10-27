#!/usr/bin/python3
import handlers
# import callbacks
# import orders
# import sms


def routes_setup():
    return [
        (r'/', handlers.Main),
        (r'/login', handlers.Login),
        (r'/logout', handlers.Logout),
        (r'/input_data', handlers.InputData),
        (r'/ws', handlers.WSHandler),
        # (r'/callback_complete/{order_id:int}', callbacks.CallbackComplete),
        # (r'/callback_start', callbacks.CallbackStart),
        # (r'/callback_startted', callbacks.CallbackStarted),
        # (r'/callback_delivered', callbacks.CallbackDelivered),
        # (r'/callback_temporary_error', callbacks.CallbackTemporaryError),
        # (r'/callback_busy', callbacks.CallbackBusy),
        # (r'/callback_answer', handlers.CallbackAns),
        # (r'/order_create', orders.OrderCreate),
        # (r'/order_created', orders.OrderCreated),
        # (r'/order_accepted', orders.OrderAccepted),
        # (r'/order_completed', orders.OrderCompleted),
        # (r'/order_aborted', orders.OrderAborted),
        # (r'/order_driver_call_client', orders.DriverCallClient),
        # (r'/order_client_gone', orders.OrderClientGone),
        # (r'/order_client_fuck', orders.OrderClientFuck),
        # (r'/sms_send', sms.SMSSend),
        # (r'/sms_sended', sms.SMSSended),
        # (r'/sms_error', sms.SMSError),
        (r'/gen/message', handlers.SMSMessage),
        (r'/gen/phrase', handlers.VoiceMessage),
        (r'/(execsvcscript.*)', handlers.TMHandler),
        ]