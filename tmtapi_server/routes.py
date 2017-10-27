#!/usr/bin/python3
import handlers


def routes_setup():
    return [
        (r'/', handlers.Main),
        (r'/change_order_state', handlers.ChangeOrderState),
        # (r'/common_api/1.0/(.*)', handlers.COMMON_API),
        (r'/common_api/1.0/get_order_state(.*)', handlers.get_order_state),
        (r'/tm_tapi/1.0/set_request_state(.*)', handlers.set_request_state),
        (r'/tm_tapi/1.0/get_info_by_order_id(.*)', handlers.get_info_by_order_id),
        ]
