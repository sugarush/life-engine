from sugar_odm import Model, Field

from . item import Item


class Equipment(Model):
    head = Field(type=Item)
    back = Field(type=Item)
    shoulders = Field(type=Item)
    chest = Field(type=Item)
    waist = Field(type=Item)
    legs = Field(type=Item)
    left = Field(type=Item)
    right = Field(type=Item)
    feet = Field(type=Item)
