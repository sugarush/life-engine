from sugar_document import Document
from sugar_api import preflight, content_type, accept, webtoken, rate, jsonapi
from sugar_api import validate, Error

from api import server
from model.character import Character
from world.cache import WorldCache

@server.options('/v1/create')
async def create(request):
    return preflight(methods=[ 'POST' ])

@server.post('/v1/create')
@content_type
@accept
@webtoken
@validate
@rate(10, 'secondly')
async def create(request, token):

    if not token:
        error = Error(
            title = 'Create Character Error',
            detail = 'You are not logged in.',
            status = 403
        )
        return jsonapi({ "errors": [ error.serialize() ] }, status=403)

    token = Document(token)

    data = request.json.get('data')
    attributes = data.get('attributes')

    character = await Character.find_one({ 'profile': token.data.id })

    if character:
        error = Error(
            title = 'Create Character Error',
            detail = 'You already have a character.',
            status = 403
        )
        return jsonapi({ "errors": [ error.serialize() ] }, status=403)

    try:
        character = Character(attributes)
    except:
        error = Error(
            title = 'Create Character Error',
            detail = 'Invalid attributes.',
            status = 403
        )
        return jsonapi({ "errors": [ error.serialize() ] }, status=403)

    character.profile = token.data.id

    if not character.race in WorldCache.races:
        error =  Error(
            title = 'Create Character Error',
            detail = 'Invalid race.',
            status = 403
        )
        return jsonapi({ "errors": [ error.serialize() ] }, status=403)

    character.level = {
        'current': 1,
        'experience': 0,
        'next': 1000
    }
    character.attributes = WorldCache.races[character.race]['attributes']
    character.health = (await character.stats)['max_health']
    character.state = {
        'target': None,
        'hostile': False,
        'retaliate': False,
        'dead': False,
        'casting': False
    }

    await character.save()

    return jsonapi({
        'data': {
            'attributes': {
                'message': 'Character created.',
                'url': f'/v1/characters/{character.id}'
            }
        }
    })
