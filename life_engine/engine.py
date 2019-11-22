from asyncio import run, sleep, create_task, CancelledError
from time import time
from uuid import uuid4
from logging import getLogger, basicConfig, INFO
basicConfig(format='%(asctime)-15s %(name)s %(message)s')

from sanic import Sanic
from colorama import Style, Fore, Back

from sugar_odm import MongoDB
from sugar_api import Redis

from model.character import Character
from decorator import character_event
from connections import Connections
from world.cache import WorldCache



class LifeEngine(object):

    server = Sanic('life.engine')
    shard = str(uuid4())
    iterator = None
    output = getLogger('life.engine')

    time = time()
    tick_radius = 50
    tick_units = 'm'
    tick_timeout = 60
    respawn = 600

    @server.listener('before_server_start')
    async def setup(app, loop):
        LifeEngine.output.setLevel(INFO)
        MongoDB.set_event_loop(loop)
        await Redis.set_event_loop(loop)
        WorldCache.set_shard(LifeEngine.shard)
        LifeEngine.LifeEngine_run = create_task(LifeEngine.run())
        LifeEngine.output.info(f'{Fore.GREEN}Started Life Engine iterator.{Style.RESET_ALL}')
        LifeEngine.WorldCache_init = create_task(WorldCache.init())
        LifeEngine.output.info(f'{Fore.GREEN}Started Life Engine world cache.{Style.RESET_ALL}')

    @server.listener('before_server_stop')
    async def teardown(app, loop):
        LifeEngine.LifeEngine_run.cancel()
        try:
            await LifeEngine.LifeEngine_run
        except CancelledError:
            LifeEngine.output.info(f'{Fore.GREEN}Stopped Life Engine iterator.{Style.RESET_ALL}')
        LifeEngine.WorldCache_init.cancel()
        try:
            await LifeEngine.WorldCache_init
        except CancelledError:
            pass
        await WorldCache.close()
        MongoDB.close()
        await Redis.close()

    @classmethod
    async def run(cls):
        while True:
            cls.time = time()
            await cls.iterate()
            await sleep(cls.tick_timeout)

    @classmethod
    async def iterate(cls):
        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
        start = time()
        async for key, _ in redis.izscan('location', match=f'{cls.shard}:*'):
            split = key.split(b':')
            shard = split[0]
            key = split[1]
            await cls.tick(key)
        end = time()
        if (end - start) > cls.tick_timeout:
            cls.output.error(f'{Fore.RED}Server is lagging due to too many users.{Style.RESET_ALL}')
            cls.output.error(f'{Fore.RED}Currently experiencing a time dilation of: {(end - start)}s.{Style.RESET_ALL}')

    @classmethod
    async def tick(cls, key):
        this = await Character.find_by_id(key.decode())

        if this:
            if this.state.dead:
                if time() - this.state.dead > cls.respawn:
                    if not this.email:
                        await this.revive()
                return
            else:
                await this.regenerate()

        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
        result = await redis.georadiusbymember('position', key, cls.tick_radius, unit=cls.tick_units)

        for _key in result:

            if key == _key:
                continue

            other = await Character.find_by_id(_key.decode())
            await cls.interact(this, other)
            await cls.step(this, other)

    @classmethod
    async def interact(cls, this, other):
        if this and other:
            # A player is interacting with another player
            if this.email and other.email:
                pass
            # A player is interacting with a mob
            elif this.email and not other.email:
                pass
            # A mob is interacting with a player
            elif not this.email and other.email:
                if this.state.hostile and not this.state.target:
                    await this.target(other)
            # Mobs do not interact with other mobs
            elif not this.email and not other.email:
                pass

    @classmethod
    async def step(cls, this, other):
            if this.state.target:
                await this.attack()

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
        await cls.set_character_location(event, character)

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
