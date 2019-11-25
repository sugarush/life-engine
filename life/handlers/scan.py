from sugar_api import preflight, content_type, webtoken, rate, jsonapi
from sugar_api import Redis

from api import server
from world.cache import WorldCache


@server.options('/v1/scan/<longitude>/<latitude>/<radius>/<units>')
async def scan(request, **kargs):
    return preflight(methods=[ 'GET' ])

@server.get('/v1/scan/<longitude>/<latitude>/<radius>/<units>')
@content_type
@webtoken
@rate(5, 'secondly')
async def scan(request, longitude, latitude, radius, units, token):
    redis = await Redis.connect(host='redis://localhost', minsize=1, maxsize=1)
    result = await redis.georadius('location', longitude, latitude, float(radius), unit=units)

    oids = [ ]

    for key in result:

        split = key.split(b':')
        shard = split[0]
        oid = split[1]

        oids.append(oid)

    return jsonapi({
        'data': {
            'attributes': {
                'characters': oids
            }
        }
    })
