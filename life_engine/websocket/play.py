import jwt

from sugar_document import Document

from engine import LifeEngine as LE
from connections import Connections


@LE.server.websocket('/v1/play')
async def v1_play(request, socket):
    socket.send({
        'type': 'authorization-request'
    })

    response = Document(await socket.recv())

    if not response.event.type == 'authorization-response':
        await socket.close()

    if not response.data:
        await socket.close()

    if not response.data.token and isinstance(response.data.token, str):
        await socket.close()

    token = Document(jwt.decode(response.data.token, secret=LE.secret))

    Connections.set_socket_by_character_id(socket, token.character_id)
    Connections.on('login', LE.login)
    Connections.on('set-player-location', LE.set_player_location)
    Connections.on('logout', LE.logout)
