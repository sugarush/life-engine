from sugar_odm import Model, Field


class Attributes(Model):
    strength = Field(type=int)
    dexterity = Field(type=int)
    constitution = Field(type=int)
    intelligence = Field(type=int)
    wisdom = Field(type=int)
    charisma = Field(type=int)
