import os
from time import time

from yaml import load

from model.character import Character

from jinja2 import Environment, FileSystemLoader, select_autoescape


class WorldCache(object):

    jinja_monsters = Environment(
        loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'monsters')),
        autoescape = select_autoescape(['yml'])
    )
    jinja_professions = Environment(
        loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'professions')),
        autoescape = select_autoescape(['yml'])
    )

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
            template = cls.jinja_professions.get_template(name)
            cls.professions[base] = load(template.render())

        path = f'monsters/{cls.country}/{cls.state}/{cls.county}'
        monsters_directory = os.path.join(cls.directory, path)

        for name in os.listdir(monsters_directory):
            cls.base = base = name.split('.')[0]
            template = cls.jinja_monsters.get_template(f'{cls.country}/{cls.state}/{cls.county}/{name}')
            cls.monsters[base] = load(template.render())
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
