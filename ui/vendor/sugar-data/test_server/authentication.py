from datetime import datetime, timedelta

from sugar_api import WebToken

from models.user import User


WebToken.set_secret('secret')


class Authentication(WebToken):

    @classmethod
    async def create(cls, attributes):
        username = attributes.get('username')

        if not username:
            raise Exception('No username provided.')

        password = attributes.get('password')

        if not password:
            raise Exception('No password provided.')

        user = await User.find_one({
            'username': username,
            'password': password
        })

        if not user:
            raise Exception('Invalid username or password.')

        return {
            'exp': datetime.utcnow() + timedelta(minutes=5),
            'nbf': datetime.utcnow(),
            'iat': datetime.utcnow(),
            'data': {
                'id': user.id,
                'groups': user.groups
            }
        }

    @classmethod
    async def refresh(cls, token):
        token_data = token.get('data')
        token_id = token_data.get('id')
        token_scope = token_data.get('scope', { })
        token_attributes = token_data.get('attributes', { })

        user = await User.find_by_id(token_id)

        if not user:
            raise Exception('User not found for token ID.')

        return {
            'exp': datetime.utcnow() + timedelta(minutes=5),
            'nbf': datetime.utcnow(),
            'iat': datetime.utcnow(),
            'data': {
                'id': token_id,
                'groups': user.groups,
                'scope': token_scope,
                'attributes': token_attributes
            }
        }
