#!/usr/bin/python3
import datetime
import psycopg2
import settings
import asyncio


EVENTS = {
    'SMS_SEND': sms_send,
    }

async def sms_send(order_data):
    pass
