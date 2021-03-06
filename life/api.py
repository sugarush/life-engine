from sanic import Sanic
from sugar_api import CORS, Redis
from sugar_odm import MongoDB

from world.cache import WorldCache

CORS.set_origins('*')

server = Sanic('life-api')

@server.listener('before_server_start')
async def before_server_start(app, loop):
    MongoDB.set_event_loop(loop)
    await Redis.set_event_loop(loop)
    Redis.default_connection(host='redis://localhost', minsize=5, maxsize=10)

@server.listener('before_server_stop')
async def before_server_stop(app, loop):
    MongoDB.close()
    await Redis.close()
