import os
from time import time
from random import random
from logging import getLogger, basicConfig, INFO
basicConfig(format='%(asctime)-15s %(name)s %(message)s')

from colorama import Fore, Back, Style
from toml import loads

from model.character import Character

from jinja2 import Environment, FileSystemLoader, select_autoescape


def coordinates(longitude, latitude, spread=0):
    longitude += spread * random()
    latitude += spread * random()
    return f'[ {longitude}, {latitude} ]'


class WorldCache(object):

    output = getLogger('life.cache')

    jinja_monsters = Environment(
        loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'monsters')),
        autoescape = select_autoescape(['toml'])
    )
    jinja_professions = Environment(
        loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'professions')),
        autoescape = select_autoescape(['toml'])
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

        cls.output.setLevel(INFO)

        globals = {
            'range': range,
            'coordinates': coordinates
        }

        filters = {

        }

        cls.jinja_monsters.globals = globals
        cls.jinja_monsters.filters = filters

        cls.jinja_professions.globals = globals
        cls.jinja_professions.filters = filters

        professions_directory = os.path.join(cls.directory, 'professions')

        for name in os.listdir(professions_directory):
            base = name.split('.')[0]
            template = cls.jinja_professions.get_template(name)
            cls.professions[base] = loads(template.render())

        path = f'monsters/{cls.country}/{cls.state}/{cls.county}'
        monsters_directory = os.path.join(cls.directory, path)

        for name in os.listdir(monsters_directory):
            cls.base = base = name.split('.')[0]
            template = cls.jinja_monsters.get_template(f'{cls.country}/{cls.state}/{cls.county}/{name}')
            cls.monsters[base] = loads(template.render())
            for m in cls.monsters[base]['monsters']:
                character = Character(m['monster'])
                character.shard = cls.shard
                await character.save()
                await character.redis_set_location(
                    character.location.coordinates[0],
                    character.location.coordinates[1]
                )
                cls.monsters[character.id] = True
                cls.output.info(f'{Fore.MAGENTA}Created {character.id}{Style.RESET_ALL}')

    @classmethod
    async def close(cls):
        for m in cls.monsters[cls.base]['monsters']:
            character = await Character.find_one({
                'shard': cls.shard,
                'world_id': m['monster']['world_id']
            })
            cls.output.info(f'{Fore.MAGENTA}Removing {character.id}{Style.RESET_ALL}')
            await character.redis_remove_location()
            await character.delete()
