from ujson import dumps

from model.character import Character

def character_event(handler):
    async def handler(socket, event):
        character = await Character.find_by_id(event.character.id)
        if character and socket is character.socket:
            await handler(character, event)
        else:
            await socket.send_json({ 'type': 'invalid-character-event' })
