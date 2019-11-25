from sugar_api import preflight, content_type, webtoken, rate, jsonapi

from api import server
from world.cache import WorldCache


@server.options('/v1/races')
async def professions(request):
    return preflight(methods=[ 'GET' ])

@server.get('/v1/races')
@content_type
@webtoken
@rate(10, 'secondly')
async def professions(request, token):
    return jsonapi({
        'data': {
            'attributes': WorldCache.races
        }
    })
