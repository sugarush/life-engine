from sugar_odm import MongoDBModel, Model, Field

from . attributes import Attributes
from . resistances import Resistances


class Profession(MongoDBModel):
    title = Field(required=True)
    attributes = Field(type=Attributes, required=True)
    resistances = Field(type=Resistances, required=True)
