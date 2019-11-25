import jwt
from ujson import loads, dumps

from sugar_document import Document

from play import PlayServer as PS
from connections import Connections


@PS.server.websocket('/v1/play')
async def v1_play(request, socket):
    await socket.send(dumps({
        'type': 'authorization-request'
    }))

    response = Document(loads(await socket.recv()))

    if not response.event.type == 'authorization-response':
        await socket.close()

    if not response.data:
        await socket.close()

    if not response.data.token and isinstance(response.data.token, str):
        await socket.close()

    token = Document(jwt.decode(response.data.token, secret=PS.secret))

    Connections.set_socket_by_character_id(socket, token.data.character.id)

    socket = Connections.socket_by_character_id(token.data.character.id)

    socket.disconnect = PS.disconnect
    Connections.on('reconnect', PS.reconnect)
    Connections.on('login', PS.login)
    Connections.on('logout', PS.logout)

    Connections.on('player-set-location', PS.player_location)
    Connections.on('player-request-stats', PS.player_request_stats)
