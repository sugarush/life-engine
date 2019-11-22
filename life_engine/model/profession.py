from sugar_odm import Model, Field

from . attributes import Attributes
from . resistances import Resistances


class Profession(Model):
    title = Field(required=True)
