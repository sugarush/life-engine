from model.character import Character

def character_event(handler):
    async def handler(event):
        character = await Character.find_by_id(event.character.id)
        await handler(character, event)
