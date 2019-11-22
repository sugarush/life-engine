from time import time
from copy import deepcopy
from collections import Counter

from sugar_odm import MongoDBModel, Model, Field
from sugar_api import Redis, JSONAPIMixin

from connections import Connections

from . item import Item
from . equipment import Equipment
from . attributes import Attributes
from . resistances import Resistances
from . profession import Profession
from . state import State
from . name import Name
from . level import Level


class Character(MongoDBModel, JSONAPIMixin):

    __set__ = {
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
        'level': [ ]
    }

    profile = Field()
    name = Field(type=Name, required=True)
    title = Field()
    profession = Field(type=Profession, required=True)
    attributes = Field(type=Attributes)
    resistances = Field(type=Resistances)
    equipment = Field(type=Equipment)
    inventory = Field(type=[ Item ])
    state = Field(type=State, required=True)
    health = Field(type=int, required=True)
    level = Field(type=Level, required=True)

    @property
    async def stats(self):
        profession = await Profession.find_one({
            'title': self.profession.title
        })

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

        health = attributes['constitution'] * 10
        hit = attributes['dexterity']

        return {
            'armor': armor,
            'health': health,
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

    @property
    def client_id(self):
        return f'{self.shard}:{self.id}'

    async def set_shard(self, name):
        self.shard = name
        await self.save()

    async def location(self):
        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
        coordinates = await redis.geopos('position', self.client_id)

    async def set_location(self, longitude, latitude):
        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
        await redis.geoadd('position', longitude, latitude, self.client_id)

    async def remove_location(self):
        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
        await redis.zrem('position', self.client_id)

    async def target(self, other):
        self.state.target = other.id
        await self.save()
        if other.state.retaliate:
            await other.target(self)

    async def untarget(self):
        self.state.target = None
        await self.save()

    async def attack(self):
        other = await Character.find_by_id(self.state.target)
        other.health -= 5 * ((await self.stats)['attributes']['strength'] / 10)
        if other.health <= 0:
            other.state.dead = time()
            other.state.target = None
            await self.killing_blow(other)
        await other.save()

    async def killing_blow(self, other):
        self.add_experience(other.level.experience)
        await self.untarget()

    def add_experience(self, experience):
        self.level.experience += experience
        if self.level.next and (self.level.experience >= self.level.next):
            self.level_up()

    def level_up(self):
        pass
