from api import server
from model.character import Character

server.blueprint(Character.resource(url_prefix='v1'))
