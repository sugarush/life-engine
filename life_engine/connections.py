from asyncio import create_task, CancelledError
from ujson import dumps
from sanic.websocket import WebSocketConnection


class LifeSocket(WebSocketConnection):

    def __init__(self, websocket):
        self._send = websocket._send
        self._receive = websocket.receive

    async def json(self, data):
        await self.send(dumps(data))

    async def recv(self, *args, **kwargs) -> Optional[str]:
        message = await self._receive()

        if message["type"] == "websocket.receive":
            return message["text"]
        elif message["type"] == "websocket.disconnect":
            await self.disconnect(self)

        return None


class Connections(object):

    characters = { }
    tasks = { }
    handlers = { }
    sockets = { }

    @classmethod
    def on(cls, event, callback):
        cls.handlers[event] = callback

    @classmethod
    def socket_by_character_id(cls, id):
        return cls.characters[id]

    @classmethod
    def character_id_by_socket(cls, socket):
        return cls.sockets[socket]

    @classmethod
    async def set_socket_by_character_id(cls, socket, id):
        socket = LifeSocket(socket)
        socket[socket] = id
        socket.disconnect = cls.handle_disconnect
        cls.characters[id] = socket

        async def watch(socket):
            while True:
                event = Document(await socket.recv())
                if event.character.id:
                    cls.process_client_event(socket, event)

        cls.tasks[id] = create_task(watch(socket))

    @classmethod
    async def process_client_event(cls, socket, event):
        if event.type in cls.handlers:
            await cls.handlers[event.type](event)

    @classmethod
    async def close(cls):
        for id, task in cls.tasks:
            task.close()
            try:
                await task
            except CancelledError:
                pass
