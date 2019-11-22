import os

from yaml import load
from yaml import Loader

from model.character import Character


class WorldCache(object):

    directory = os.path.dirname(__file__)

    country = None
    state = None
    county = None

    monsters = { }
    professions = { }

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
            base = name.split('.')[0]
            file = open(os.path.join(monsters_directory, name))
            cls.monsters[base] = load(file, Loader=Loader)
