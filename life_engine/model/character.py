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

    shard = Field()
    monster_id = Field()
    profile = Field()
    name = Field(type=Name, required=True)
    title = Field()
    race = Field(required=True)
    profession = Field(required=True)
    attributes = Field(type=Attributes, required=True)
    equipment = Field(type=Equipment)
    inventory = Field(type=[ Item ])
    state = Field(type=State, required=True)
    health = Field(type=int, required=True)
    level = Field(type=Level, required=True)
    location = Field(type=Location)
    touched = Field(type='timestamp')

    @property
    def socket(self):
        return Connections.socket_by_character_id(self.id)

    @property
    def connected(self):
        return self.socket

    async def set_location(self, longitude, latitude):
        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
        await redis.geoadd('location', longitude, latitude, f'{self.shard}:{self.id}')
        self.longitude = longitude
        self.latitude = latitude
        await self.save()

    async def remove_location(self):
        redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
        await redis.zrem('location', f'{self.shard}:{self.id}')
        self.longitude = None
        self.latitude = None
        await self.save()
