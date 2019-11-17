import asyncio
import uvloop
from random import random

from sugar_api import Redis

from model.character import Character
from engine import LifeEngine

class Engine(LifeEngine):

    ogres = [ ]
    samael = None

    @classmethod
    async def setup(cls):

        for i in range(0, 1):

            ogre = Character({
                'name': {
                    'first': 'Ogre'
                },
                'profession': 'Warrior',
                'level': {
                    'current': 1,
                    'experience': 500
                },
                'health': {
                    'current': 100,
                    'max': 100
                },
                'attributes': {
                    'strength': 10,
                    'dexterity': 5,
                    'agility': 5,
                    'constitution': 10
                },
                'resistances': {
                    'fire': 0,
                    'frost': 0,
                    'holy': 0,
                    'shadow': 0
                },
                'state': {
                    'hostile': True
                }
            })

            cls.ogres.append(ogre)

            await ogre.save()
            #await ogre.set_location(42.4091595 + random() / 1000, -84.5396023 + random() / 1000)
            await ogre.set_location(42.4091595, -84.5396023)

        cls.samael = samael = Character({
            'email': 'paul.severance@gmail.com',
            'name': {
                'first': 'Samael'
            },
            'profession': 'Warrior',
            'level': {
                'current': 10,
                'experience': 50000,
                'next': 75000
            },
            'health': {
                'current': 500,
                'max': 500
            },
            'attributes': {
                'strength': 50,
                'dexterity': 50,
                'agility': 50,
                'constitution': 50
            },
            'resistances': {
                'fire': 50,
                'frost': 50,
                'holy': 100,
                'shadow': 50
            },
            'state': {
                'retaliate': True
            },
            'equipment': {
                'head': {
                    'title': 'Obsidian Crown',
                    'slot': 'head',
                    'attributes': {
                        'strength': 100
                    },
                    'armor': 1000
                }
            }
        })

        await samael.save()
        await samael.set_location(42.4091595, -84.5396023)

        print(await samael.modifiers())

    @classmethod
    async def teardown(cls):
        for ogre in cls.ogres:
            await ogre.remove_location()
            await ogre.delete()
        await cls.samael.delete()

loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(Engine.run(loop))
