from sugar_odm import MongoDBModel, Field
from sugar_api import JSONAPIMixin

from  . name import Name


class Profile(MongoDBModel, JSONAPIMixin):
    name = Field(type=Name)
    email = Field(required=True)
    password = Field(required=True, computed='encrypt_password')

    def encrypt_password(self):
        if self.password == 'hashed-':
            raise Exception('Invalid password.')

        if self.password.startswith('hashed-'):
            return self.password

        return f'hashed-{hashlib.sha256(self.password.encode()).hexdigest()}'
