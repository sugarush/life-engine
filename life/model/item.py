from uuid import uuid4

from sugar_odm import Model, Field

from . attributes import Attributes
from . resistances import Resistances


class Item(Model):
    title = Field()
    slot = Field()
    attributes = Field(type=Attributes)
    resistances = Field(type=Resistances)
    armor = Field(type=int)
    count = Field(type=int)
