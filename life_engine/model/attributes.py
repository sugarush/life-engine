from sugar_odm import Model, Field


class Attributes(Model):
    strength = Field(type=int)
    dexterity = Field(type=int)
    agility = Field(type=int)
    constitution = Field(type=int)
