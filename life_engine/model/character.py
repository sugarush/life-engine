from time import time
from uuid import uuid4
from copy import deepcopy
from collections import Counter

from sugar_odm import MongoDBModel, Model, Field
from sugar_api import Redis

from . item import Item
from . equipment import Equipment
from . attributes import Attributes
from . resistances import Resistances
from . profession import Profession


class Level(Model):
    current = Field(type=int, required=True)
    experience = Field(type=int, required=True)
    next = Field(type=int)


class State(Model):
    target = Field()
    hostile = Field(type=bool)
    retaliate = Field(type=bool)
    dead = Field(type=int)


class Name(Model):
    first = Field(required=True)
    last = Field()


class Character(MongoDBModel):
    email = Field()
    name = Field(type=Name, required=True)
    profession = Field(required=True)
    attributes = Field(type=Attributes, required=True)
    resistances = Field(type=Resistances)
    equipment = Field(type=Equipment)
    inventory = Field(type=[ Item ])
    state = Field(type=State, required=True)
    health = Field(type=int, required=True)
    level = Field(type=Level, required=True)

    async def stats(self):
        profession = await Profession.find_one({
            'title': self.profession
        })

        attributes = Counter(self.attributes._data)
        resistances = Counter(self.resistances._data)

        attributes += Counter(profession.attributes._data)
        resistances += Counter(profession.resistances._data)

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

        return {
            'armor': armor,
            'health': health,
            'attributes': dict(attributes),
            'resistances': dict(resistances)
        }

    async def location(self):
        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
        coordinates = await redis.geopos('location', self.id)

    async def set_location(self, longitude, latitude):
        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
        await redis.geoadd('location', longitude, latitude, self.id)

    async def remove_location(self):
        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
        await redis.zrem('location', self.id)

    async def target(self, other):
        self.state.target = other.id
        await self.save()
        if other.state.retaliate:
            await other.target(self)

    async def untarget(self):
        self.state.target = None
        await self.save()

    async def attack(self):
        stats = await self.stats()
        other = await Character.find_by_id(self.state.target)
        await other.damage(5 * (stats['attributes']['strength'] / 10))

    async def damage(self, damage=0):
        other = await Character.find_by_id(self.state.target)
        self.health -= damage
        if self.health <= 0:
            self.state.dead = time()
            self.state.target = None
            await other.killing_blow(self)
        await self.save()

    async def killing_blow(self, other):
        self.add_experience(other.level.experience)
        await self.untarget()

    def add_experience(self, experience):
        self.level.experience += experience
        if self.level.experience >= self.level.next:
            self.level_up()

    def level_up(self):
        pass
