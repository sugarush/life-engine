from pymongo import GEOSPHERE

from sugar_odm import Field

from . character import Character
from . location import Location


class Monster(Character):

    __index__ = [
        {
            'keys': [('location', GEOSPHERE)]
        }
    ]

    shard = Field(required=True)
    expire = Field(required=True)
    location = Field(type=Location)
