import hashlib
from datetime import datetime, timedelta

from sugar_api import WebToken

from model.profile import Profile
from model.character import Character



class Authentication(WebToken):

    @classmethod
    async def create(cls, attributes):
        username = attributes.get('username')

        if not username:
            raise Exception('No username provided.')

        password = attributes.get('password')

        if not password:
            raise Exception('No password provided.')

        digest = f'hashed-{hashlib.sha256(password.encode()).hexdigest()}'

        profile = await Profile.find_one({
            'username': username,
            'password': digest
        })

        if not profile:
            raise Exception('Invalid username or password.')

        return {
            #'exp': datetime.utcnow() + timedelta(minutes=5),
            'nbf': datetime.utcnow(),
            'iat': datetime.utcnow(),
            'data': {
                'id': profile.id
            }
        }

    @classmethod
    async def refresh(cls, attributes, token):

        token_data = token.get('data')
        token_id = token_data.get('id')
        token_groups = token_data.get('groups')
        token_scope = token_data.get('scope')

        if not await Profile.exists(token_id):
            raise Exception('Profile not found for token ID.')

        token = {
            #'exp': datetime.utcnow() + timedelta(minutes=5),
            'nbf': datetime.utcnow(),
            'iat': datetime.utcnow(),
            'data': {
                'id': token_id,
                'groups': token_groups,
                'scope': token_scope,
            }
        }

        if attributes.get('character'):

            characters = [ character async for character in Character.find({
                'profile': profile.id
            }) ]

            character = attributes.get('character')

            if character and isinstance(character, dict):
                id = character.get('id')
                if not id in list(map(lambda c: c.id, characters)):
                    raise Exception('Invalid request.')
                if id:
                    token['data']['attributes'] = {
                        'character': {
                            'id': id
                        }
                    }
                else:
                    raise Exception('Invalid request.')
            else:
                raise Exception('Invalid request.')

        return token
