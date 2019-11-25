from sugar_odm import Model, Field


class Name(Model):
    first = Field(required=True)
    last = Field()
    title = Field()
