from sugar_odm import Model, Field


class Location(Model):
    type = Field(required=True)
    coordinates = Field(type=list, required=True)
