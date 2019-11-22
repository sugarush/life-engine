from asyncio import run, sleep, create_task, CancelledError
from time import time
from uuid import uuid4

from sanic import Sanic
from colorama import Style, Fore, Back

from sugar_odm import MongoDB
from sugar_api import Redis

from model.character import Character


class LifeEngine(object):

    server = Sanic('life-engine')
    shard = str(uuid4())
    secret = str(uuid4())
    iterator = None

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
            await cls.iterate('location')
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

            if this.state.target:
                await this.attack()
