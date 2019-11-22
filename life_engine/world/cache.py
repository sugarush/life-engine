import os
from time import time
from random import random
from logging import getLogger, basicConfig, INFO
basicConfig(format='%(asctime)-15s %(name)s %(message)s')

from colorama import Fore, Back, Style
from yaml import load, Loader

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

        cls.output.setLevel(INFO)
        cls.output.info(cls.jinja_monsters.globals)

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
            cls.professions[base] = load(template.render(), Loader=Loader)

        path = f'monsters/{cls.country}/{cls.state}/{cls.county}'
        monsters_directory = os.path.join(cls.directory, path)

        for name in os.listdir(monsters_directory):
            cls.base = base = name.split('.')[0]
            template = cls.jinja_monsters.get_template(f'{cls.country}/{cls.state}/{cls.county}/{name}')
            cls.monsters[base] = load(template.render(), Loader=Loader)
            for m in cls.monsters[base]:
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
        for data in cls.monsters[cls.base]:
            cls.output.info('%s %s', cls.shard, data['monster']['world_id'])
            character = await Character.find_one({
                'shard': cls.shard,
                'world_id': data['monster']['world_id']
            })
            await character.redis_remove_location()
            await character.delete()
