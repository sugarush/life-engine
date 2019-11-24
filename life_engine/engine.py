from asyncio import run, sleep, create_task, CancelledError
from time import time
from uuid import uuid4
from datetime import datetime
from collections import Counter
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
    shard = None
    iterator = None
    output = getLogger('life.engine')

    time = time()
    tick_radius = 50
    tick_units = 'm'
    tick_timeout = 10
    respawn = 600

    @server.listener('before_server_start')
    async def setup(app, loop):
        WorldCache.init()
        WorldCache.init_spells()
        LifeEngine.output.setLevel(INFO)
        MongoDB.set_event_loop(loop)
        await Redis.set_event_loop(loop)
        LifeEngine.LifeEngine_run = create_task(LifeEngine.run())
        LifeEngine.output.info(f'{Fore.GREEN}Started Life Engine iterator.{Style.RESET_ALL}')

    @server.listener('before_server_stop')
    async def teardown(app, loop):
        LifeEngine.LifeEngine_run.cancel()
        try:
            await LifeEngine.LifeEngine_run
        except CancelledError:
            LifeEngine.output.info(f'{Fore.GREEN}Stopped Life Engine iterator.{Style.RESET_ALL}')
        MongoDB.close()
        await Redis.close()

    @classmethod
    def configure(cls, args):
        cls.shard = args.shard

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
            oid = split[1]
            await cls.tick(oid)
        end = time()
        cls.output.info(f'{Fore.BLUE}Processing took: %ds{Style.RESET_ALL}', (end - start))
        if (end - start) > cls.tick_timeout:
            cls.output.error(f'{Fore.RED}Currently experiencing a time dilation of: {(end - start) - cls.tick_timeout}s.{Style.RESET_ALL}')

    @classmethod
    async def tick(cls, oid):
        this = await Character.find_by_id(oid.decode())

        if this:
            if this.state.dead:
                if time() - this.state.dead > cls.respawn:
                    await cls.character_revive(this)
                return
            else:
                await cls.character_regenerate(this)

            redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
            try:
                result = await redis.georadiusbymember('location', f'{cls.shard}:{key.decode()}', cls.tick_radius, unit=cls.tick_units)
            except Exception:
                return None

            for _key in result:

                if key == _key:
                    continue

                split = _key.split(b':')
                shard = split[0]
                _oid = split[1]

                other = await Character.find_by_id(_oid.decode())

                if this and other:
                    # A player is interacting with another player
                    if this.monster_id and other.monster_id:
                        pass
                    # A player is interacting with a mob
                    elif this.monster_id and not other.monster_id:
                        pass
                    # A mob is interacting with a player
                    elif not this.monster_id and other.monster_id:
                        if this.state.hostile and not this.state.target:
                            await cls.character_target(this, other)
                    # Mobs do not interact with other mobs
                    elif not this.monster_id and not other.monster_id:
                        pass

                    await other.save()

            if this.montser_id:
                if this.state.target:
                    pass # XXX: This is where attack was.
                if not this.state.dead:
                    await cls.character_wander(this)

            await this.save()

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

    @classmethod
    async def character_touch(cls, character):
        character.touched = datetime.now()
        await character.save()

    @classmethod
    async def character_stats(cls, character):
        attributes = Counter(character.attributes._data)
        resistances = Counter()

        armor = 0

        if character.equipment:
            for field in Equipment._fields:
                item = self.equipment.get(field.name)
                if item:
                    if item.attributes:
                        attributes += Counter(item.attributes._data)
                    if item.resistances:
                        resistances += Counter(item.resistances._data)
                    if item.armor:
                        armor += item.armor

        max_health = character.attributes['constitution'] * 10

        return {
            'armor': armor,
            'health_maximum': max_health,
            'attributes': dict(attributes),
            'resistances': dict(resistances)
        }

    @classmethod
    async def character_target(cls, character, target):
        character.state.target = target.id
        if target.state.retaliate:
            target.target(character)

    @classmethod
    async def character_untarget(cls, character):
        character.state.target = None

    @classmethod
    async def character_revive(cls, character):
        stats = await cls.character_stats(character)
        character.health = stats['health_maximum']

    @classmethod
    async def character_regenerate(cls, character):
        stats = await cls.character_stats(character)
        if character.health < stats['health_maximum']:
            character.health += 1

    @classmethod
    async def character_wander(cls, character):
        pass
