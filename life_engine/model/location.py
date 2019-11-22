from sugar_odm import Model, Field


class Location(Model):
    type = Field()
    coordinates = Field(type=list)
