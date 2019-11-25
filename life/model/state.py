from sugar_odm import Model, Field


class State(Model):
    target = Field()
    hostile = Field(type=bool)
    retaliate = Field(type=bool)
    dead = Field(type=int)
    casting = Field(type=bool)
