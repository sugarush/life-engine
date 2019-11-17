from time import time, sleep

import yaml

from sugar_odm import MongoDB
from sugar_api import Redis

from model.character import Character


class LifeEngine(object):

    professions = None

    @classmethod
    async def setup(cls):
        pass

    @classmethod
    async def teardown(self):
        pass

    @classmethod
    async def run(cls, loop):
        MongoDB.set_event_loop(loop)
        await Redis.set_event_loop(loop)

        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)

        await cls.setup()

        try:
            print('LifeEngine starting...')
            while True:
                async for key, _ in redis.izscan('location'):
                    await cls.tick(key)
                sleep(5)
        except KeyboardInterrupt:
            await cls.teardown()
            print('LifeEngine exiting...')

    @classmethod
    async def tick(cls, key):
        this = await Character.find_by_id(key.decode())

        if this:
            if this.state.dead:
                if time() - this.state.dead > 300:
                    if not this.email:
                        await this.delete()
                return
            else:
                stats = await this.stats()
                if this.health < stats['health']:
                    await this.damage(-1)

        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
        result = await redis.georadiusbymember('location', key, 50, unit='m')

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
