import jwt
from ujson import loads, dumps

from sugar_document import Document

from engine import LifeEngine as LE
from connections import Connections


@LE.server.websocket('/v1/play')
async def v1_play(request, socket):
    socket.send(dumps({
        'type': 'authorization-request'
    }))

    response = Document(loads(await socket.recv()))

    if not response.event.type == 'authorization-response':
        await socket.close()

    if not response.data:
        await socket.close()

    if not response.data.token and isinstance(response.data.token, str):
        await socket.close()

    token = Document(jwt.decode(response.data.token, secret=LE.secret))

    Connections.set_socket_by_character_id(socket, token.data.character.id)

    socket = Connections.socket_by_character_id(token.data.character.id)

    socket.disconnect = LE.disconnect
    Connections.on('reconnect', LE.reconnect)
    Connections.on('login', LE.login)
    Connections.on('logout', LE.logout)

    Connections.on('set-player-location', LE.set_player_location)
