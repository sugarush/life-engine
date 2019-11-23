import asyncio
from time import time
from copy import deepcopy
from collections import Counter
from datetime import datetime

from pymongo import GEOSPHERE, ASCENDING

from sugar_odm import MongoDBModel, Model, Field
from sugar_api import Redis, JSONAPIMixin, TimestampMixin

from connections import Connections

from . item import Item
from . equipment import Equipment
from . attributes import Attributes
from . resistances import Resistances
from . profession import Profession
from . state import State
from . name import Name
from . level import Level
from . location import Location


class Character(MongoDBModel, JSONAPIMixin, TimestampMixin):

    __index__ = [
        {
            'keys': [('location', GEOSPHERE)]
        }
    ]

    __set__ = {
        'shard': [ ],
        'monster_id': [ ],
        'profile': [ ],
        'name': [ ],
        'title': [ ],
        'profession': [ ],
        'attributes': [ ],
        'resistances': [ ],
        'equipment': [ ],
        'inventory': [ ],
        'state': [ ],
        'health': [ ],
        'level': [ ],
        'location': [ ],
        'touched': [ ]
    }

    shard = Field(required=True)
    monster_id = Field()
    profile = Field()
    name = Field(type=Name, required=True)
    title = Field()
    profession = Field(type=Profession, required=True)
    attributes = Field(type=Attributes, required=True)
    resistances = Field(type=Resistances, required=True)
    equipment = Field(type=Equipment)
    inventory = Field(type=[ Item ])
    state = Field(type=State, required=True)
    health = Field(type=int, required=True)
    level = Field(type=Level, required=True)
    touched = Field(type='timestamp')
    location = Field(type=Location)

    async def touch(self):
        self.touched = datetime.now()
        await self.save()

    def is_monster(self):
        return self.monster_id and True

    def is_player(self):
        return (not self.monster_id) and True

    @property
    async def stats(self):
        attributes = Counter(self.attributes._data)
        resistances = Counter(self.resistances._data)

        armor = 0

        if self.equipment:
            for field in Equipment._fields:
                item = self.equipment.get(field.name)
                if item:
                    if item.attributes:
                        attributes += Counter(item.attributes._data)
                    if item.resistances:
                        resistances += Counter(item.resistances._data)
                    if item.armor:
                        armor += item.armor

        max_health = self.attributes['constitution'] * 10

        return {
            'armor': armor,
            'max_health': max_health,
            'attributes': dict(attributes),
            'resistances': dict(resistances)
        }

    @property
    def socket(self):
        if self.connected:
            return Connections.socket_by_character_id(self.id)
        return None

    @property
    def connected(self):
        return not self.shard is None

    async def set_shard(self, name):
        self.shard = name
        await self.save()

    async def set_location(self, longitude, latitude):
        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
        await redis.geoadd('location', longitude, latitude, f'{self.shard}:{self.id}')
        self.longitude = longitude
        self.latitude = latitude

    async def remove_location(self):
        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
        await redis.zrem('location', f'{self.shard}:{self.id}')
        self.longitude = None
        self.latitude = None
        await self.save()

    def target(self, other):
        self.state.target = other.id
        if other.state.retaliate:
            other.target(self)

    def untarget(self):
        self.state.target = None

    async def revive(self):
        self.health = (await self.stats)['max_health']

    async def regenerate(self):
        if self.health < (await self.stats)['max_health']:
            self.health += 1
            await self.save()

    async def attack(self):
        other = await Character.find_by_id(self.state.target)
        other.health -= 5 * ((await self.stats)['attributes']['strength'] / 10)
        if other.health <= 0:
            other.state.dead = time()
            other.state.target = None
            await self.killing_blow(other)
        await other.save()

    async def wander(self):
        pass

    async def killing_blow(self, other):
        self.add_experience(other.level.experience)
        await self.untarget()

    def add_experience(self, experience):
        self.level.experience += experience
        if self.level.next and (self.level.experience >= self.level.next):
            self.level_up()

    def level_up(self):
        pass
