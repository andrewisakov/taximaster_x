#!/usr/bin/python3
import aiohttp_debugtoolbar
import aiohttp_autoreload
from aiohttp_debugtoolbar import toolbar_middleware_factory
from aiohttp import web
import asyncio
import aiopg
# from routes import routes_setup
import handlers
import settings


async def init_pg():
    return await aiopg.create_pool(dsn=settings.PG_DSN)


async def close_pg(app):
    app['postgres'].close()
    await app['postgres'].wait_closed


loop = asyncio.get_event_loop()
app = web.Application(loop=loop, logger=settings.logger_,
                      middlewares=[toolbar_middleware_factory])
aiohttp_debugtoolbar.setup(app)
app['postgres'] = loop.run_until_complete(init_pg())
app.on_cleanup.append(close_pg)
app.router.add_get('/distributor/{phone:\d+}/{lock:\d{1}}', handlers.distributor)
app.router.add_get('/unlock/{distributor:\w+}', handlers.distributor_unlock)
app.router.add_get('/smsc/{phone:\d+}', handlers.smsc)
app.router.add_get('/drop', handlers.drop_cache)
app.router.add_get('/show', handlers.show_cache)
# web.run(app)
if settings.DEBUG:
    aiohttp_autoreload.start()
f = loop.create_server(app.make_handler(debug=settings.DEBUG), '0.0.0.0', settings.PORT)
srv = loop.run_until_complete(f)
loop.run_forever()
