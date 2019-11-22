from sugar_odm import MongoDBModel, Field
from sugar_api import JSONAPIMixin


class User(MongoDBModel, JSONAPIMixin):

    __acl__ = {
        'self': ['read', 'update'],
        'administrator': ['all'],
        'other': ['read']
    }

    __set__ = {
        'groups': ['administrator']
    }

    username = Field(required=True)
    password = Field(required=True)

    groups = Field(type=list)
