#!/usr/bin/python3
import handlers


def routes_setup():
    return [
        (r'/', handlers.Main),
        (r'/change_order_state', handlers.ChangeOrderState),
        (r'/common_api/1.0/(.*)', handlers.COMMON_API),
        (r'/tm_tapi/1.0/(.*)', handlers.TM_TAPI),
        ]
