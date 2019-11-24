from sugar_odm import Model, Field


class Resistances(Model):
    fire = Field(type=int)
    frost = Field(type=int)
    poison = Field(type=int)
    shadow = Field(type=int)
    magic = Field(type=int)
    holy = Field(type=int)
