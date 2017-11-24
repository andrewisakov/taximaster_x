#!/usr/bin/python3
import handlers


def routes_setup():
    return [
        (r'/distributor/(\d+)', handlers.Distributor),
        (r'/smsc/(\d+)', handlers.SMSC),
        # (r'/smsc_delivered/(\d+)', ),
    ]
