from asyncio import run, sleep, create_task, CancelledError
from time import time
from uuid import uuid4

from sanic import Sanic
from colorama import Style, Fore, Back

from sugar_odm import MongoDB
from sugar_api import Redis

from decorator import character_event
from model.character import Character


class LifeEngine(object):

    server = Sanic('life-engine')
    shard = str(uuid4())
    secret = str(uuid4())
    iterator = None

    time = time()
    tick_radius = 50
    tick_units = 'm'
    tick_timeout = 5
    corpse_timeout = 300

    @server.listener('before_server_start')
    async def setup(app, loop):
        LifeEngine.iterator = create_task(LifeEngine.run())
        MongoDB.set_event_loop(loop)
        await Redis.set_event_loop(loop)

    @server.listener('before_server_stop')
    async def teardown(app, loop):
        LifeEngine.iterator.cancel()
        try:
            await LifeEngine.iterator
        except CancelledError:
            print(f'{Fore.GREEN}Stopped Life Engine iterator.{Style.RESET_ALL}')
        MongoDB.close()
        await Redis.close()

    @classmethod
    async def run(cls):
        while True:
            cls.time = time()
            await cls.iterate(cls.shard)
            await sleep(cls.tick_timeout)

    @classmethod
    async def iterate(cls, table):
        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
        async for key, _ in redis.izscan(table):
            await cls.tick(key)

    @classmethod
    async def tick(cls, key):
        this = await Character.find_by_id(key.decode())

        if this:
            if this.state.dead:
                if time() - this.state.dead > cls.corpse_timeout:
                    if not this.email:
                        await this.delete()
                return
            else:
                stats = await this.stats()
                if this.health < stats['health']:
                    this.health += 1
                    await this.save()

        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
        result = await redis.georadiusbymember('location', key, cls.tick_radius, unit=cls.tick_units)

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
    @character_event
    async def login(cls, event, character):
        await character.set_shard(cls.shard)
        await cls.set_character_location(event, character)

    @classmethod
    @character_event
    async def set_character_location(cls, event, character):
        await character.set_location(event.data.longitude, event.data.latitude)
        await character.socket.send({
            'type': 'update-player-location',
            'data': {
                'longitude': events.data.longitude,
                'latitude': events.data.latitude
            }
        })

    @classmethod
    @character_event
    async def logout(cls, event, character):
        await character.remove_location()
        await character.socket.send({
            'type': 'confirm-logout',
            'data': {
                'message': 'Successfully logged out.'
            }
        })

    @classmethod
    async def disconnect(cls, socket):
        pass

    @classmethod
    @character_event
    async def reconnect(cls, event, character):
        pass
