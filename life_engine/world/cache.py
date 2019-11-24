import os
from uuid import uuid4
from time import time
from random import random
from logging import getLogger, basicConfig, INFO
basicConfig(format='%(asctime)-15s %(name)s %(message)s')

from colorama import Fore, Back, Style
from toml import loads

from sugar_document import Document

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
    jinja_races = Environment(
        loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'races')),
        autoescape = select_autoescape(['toml'])
    )

    directory = os.path.dirname(__file__)

    shard = None
    country = None
    state = None
    county = None
    base = None

    monsters = { }
    professions = { }
    races = { }

    @classmethod
    def set_shard(cls, name):
        cls.shard = name

    @classmethod
    def configure(cls, args):
        cls.country = args.country
        cls.state = args.state
        cls.county = args.county
        cls.shard = args.shard

    @classmethod
    def init(cls):
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

        cls.jinja_races.globals = globals
        cls.jinja_races.filters = filters

    @classmethod
    def init_professions(cls):

        professions_directory = os.path.join(cls.directory, 'professions')

        for name in os.listdir(professions_directory):
            base = name.split('.')[0]
            template = cls.jinja_professions.get_template(name)
            cls.professions[base] = loads(template.render())

    @classmethod
    def init_races(cls):

        races_directory = os.path.join(cls.directory, 'races')

        for name in os.listdir(races_directory):
            base = name.split('.')[0]
            template = cls.jinja_races.get_template(name)
            cls.races[base] = loads(template.render())

    @classmethod
    async def inint_monsters(cls):

        if not cls.country:
            raise Exception('WorldCache.init_monsters: Run configure before init_monsters.')

        path = f'monsters/{cls.country}/{cls.state}/{cls.county}'
        monsters_directory = os.path.join(cls.directory, path)

        template = cls.jinja_monsters.get_template(f'{cls.country}/{cls.state}/{cls.county}/{cls.shard}.toml')
        template_data = loads(template.render())
        for m in template_data['monsters']:
            character = Character(m['monster'])
            character.shard = cls.shard
            character.monster_id = str(uuid4())
            await character.save()
            await character.set_location(
                character.location.coordinates[0],
                character.location.coordinates[1]
            )
            cls.monsters[character.id] = True
            cls.output.info(f'{Fore.MAGENTA}Created {character.id}{Style.RESET_ALL}')

    @classmethod
    async def remove_monsters(cls):
        for oid in cls.monsters.keys():
            character = await Character.find_by_id(oid)
            cls.output.info(f'{Fore.MAGENTA}Removing {character.id}{Style.RESET_ALL}')
            await character.remove_location()
            await character.delete()
