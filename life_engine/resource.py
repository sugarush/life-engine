from api import server
from authentication import Authentication
from model.character import Character
from model.profile import Profile

server.blueprint(Authentication.resource(url_prefix='v1'))

server.blueprint(Profile.resource(url_prefix='v1'))
server.blueprint(Character.resource(url_prefix='v1'))
