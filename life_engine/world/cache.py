import os
from time import time

from yaml import load
from yaml import Loader

from model.character import Character


class WorldCache(object):

    directory = os.path.dirname(__file__)

    shard = None
    country = None
    state = None
    county = None
    base = None

    monster_layout = { }
    monsters = { }
    professions = { }

    @classmethod
    def set_shard(cls, name):
        cls.shard = name

    @classmethod
    def configure(cls, args):
        cls.country = args.country
        cls.state = args.state
        cls.county = args.county

    @classmethod
    async def init(cls):
        if not cls.country:
            raise Exception('WorldCache.init: Run configure before init.')

        professions_directory = os.path.join(cls.directory, 'professions')

        for name in os.listdir(professions_directory):
            base = name.split('.')[0]
            file = open(os.path.join(professions_directory, name))
            cls.professions[base] = load(file, Loader=Loader)

        path = f'monsters/{cls.country}/{cls.state}/{cls.county}'
        monsters_directory = os.path.join(cls.directory, path)

        for name in os.listdir(monsters_directory):
            cls.base = base = name.split('.')[0]
            file = open(os.path.join(monsters_directory, name))
            cls.monsters[base] = load(file, Loader=Loader)
            for m in cls.monsters[base]:
                character = Character(m['monster'])
                character.shard = cls.shard
                await character.save()
                await character.touch()
                await character.redis_set_location(
                    character.location.coordinates[0],
                    character.location.coordinates[1]
                )
                cls.monsters[character.id] = True

    @classmethod
    async def close(cls):
        for data in cls.monsters[cls.base]:
            print(cls.shard, data['monster']['world_id'])
            character = await Character.find_one({
                'shard': cls.shard,
                'world_id': data['monster']['world_id']
            })
            await character.redis_remove_location()
            await character.delete()
