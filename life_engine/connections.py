from asyncio import create_task, CancelledError


class Connections(object):

    sockets = { }
    tasks = { }
    handlers = { }

    @classmethod
    def on(cls, event, callback):
        cls.handlers[event] = callback

    @classmethod
    def socket_by_character_id(cls, id):
        return cls.sockets[id]

    @classmethod
    async def set_socket_by_character_id(cls, socket, id):
        cls.sockets[id] = socket

        async def watch(socket):
            while True:
                event = Document(await socket.recv())
                if event.character.id:
                    cls.process_client_event(event)

        cls.tasks[id] = create_task(watch(socket))

    @classmethod
    async def process_client_event(cls, event):
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
