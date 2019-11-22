from sugar_odm import Model, Field


class Level(Model):
    current = Field(type=int, required=True)
    experience = Field(type=int, required=True)
    next = Field(type=int)
