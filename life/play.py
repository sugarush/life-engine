from sanic import Sanic

from logging import getLogger, basicConfig, INFO
basicConfig(format='%(asctime)-15s %(name)s %(message)s')

from sugar_odm import MongoDB
from sugar_api import Redis

from decorator import character_event
from world.cache import WorldCache

class PlayServer(object):

    output = getLogger('life.playserver')
    server = Sanic('life.playserver')
    shard = None

    @server.listener('before_server_start')
    async def setup(app, loop):
        WorldCache.init()
        WorldCache.init_spells()
        WorldCache.init_professions()
        MongoDB.set_event_loop(loop)
        await Redis.set_event_loop(loop)
        PlayServer.output.setLevel(INFO)

    @server.listener('before_server_stop')
    async def teardown(app, loop):
        MongoDB.close()
        await Redis.close()

    @classmethod
    def configure(cls, args):
        cls.shard = args.shard

    @classmethod
    async def disconnect(cls, socket):
        character = await \
            Character.find_by_id(Connections.character_id_by_socket(socket))
        await character.remove_location()

    @classmethod
    @character_event
    async def reconnect(cls, event, character):
        await character.set_location(event.data.longitude, event.data.latitude)

    @classmethod
    @character_event
    async def login(cls, event, character):
        await character.set_shard(cls.shard)
        await character.player_update_stats()

    @classmethod
    @character_event
    async def logout(cls, event, character):
        await character.remove_location()
        await character.socket.send_json({
            'type': 'logout',
            'data': {
                'message': 'Successfully logged out.'
            }
        })

    @classmethod
    @character_event
    async def player_set_location(cls, event, character):
        await character.set_location(event.data.longitude, event.data.latitude)
        await character.socket.send_json({
            'type': 'player-update-location',
            'data': {
                'longitude': events.data.longitude,
                'latitude': events.data.latitude
            }
        })

    @classmethod
    @character_event
    async def player_request_stats(cls, event, character):
        await character.socket.send_json({
            'type': 'player-update-stats',
            'data': await character.stats
        })
