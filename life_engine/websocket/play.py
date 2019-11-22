from engine import LifeEngine


@LifeEngine.server.websocket('/v1/play')
async def v1_play(request, socket):
    pass
