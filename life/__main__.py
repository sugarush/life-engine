import argparse, sys

from colorama import Fore, Back, Style

parser = argparse.ArgumentParser(description='life')
subparsers = parser.add_subparsers(help='command help', dest='command')
api_parser = subparsers.add_parser('api', help='api help')
websocket_parser = subparsers.add_parser('websocket', help='websocket help')
engine_parser = subparsers.add_parser('engine', help='engine help')
world_parser = subparsers.add_parser('world', help='world help')

api_parser.add_argument('-H', '--host', default='localhost')
api_parser.add_argument('-p', '--port', default='8000')

websocket_parser.add_argument('-H', '--host', default='localhost')
websocket_parser.add_argument('-p', '--port', default='8001')

engine_parser.add_argument('-H', '--host', default='localhost')
engine_parser.add_argument('-p', '--port', default='8000')
engine_parser.add_argument('-s', '--shard', required=True)

world_parser.add_argument('-a', '--country', required=True)
world_parser.add_argument('-b', '--state', required=True)
world_parser.add_argument('-c', '--county', required=True)
world_parser.add_argument('-s', '--shard', required=True)

if len(sys.argv) == 1:
    parser.print_help()

args = parser.parse_args()

from sugar_api import WebToken


WebToken.set_secret('secret')

if args.command == 'api':

    import resource

    import handlers
    from api import server
    from world.cache import WorldCache as WC

    WC.init()
    WC.init_professions()
    WC.init_races()
    WC.init_spells()

    from logging import getLogger, basicConfig, INFO
    basicConfig(format='%(asctime)-15s %(name)s %(message)s')

    logger = getLogger('life.api')
    logger.setLevel(INFO)

    logger.info(f'{Fore.GREEN}Starting Life API Server...{Style.RESET_ALL}')
    server.run(host=args.host, port=args.port)
    logger.info(f'{Fore.GREEN}Stopping Life API Server...{Style.RESET_ALL}')
elif args.command == 'websocket':
    from sanic.websocket import WebSocketProtocol

    import websocket
    from play import PlayServer as PS

    PS.configure(args)

    PS.output.info(f'{Fore.GREEN}Starting Life Play Server...{Style.RESET_ALL}')
    PS.server.run(host=args.host, port=args.port, protocol=WebSocketProtocol)
    PS.output.info(f'{Fore.GREEN}Stopping Life Play Server...{Style.RESET_ALL}')
elif args.command == 'engine':
    import uvloop, asyncio
    from logging import INFO

    from sanic.websocket import WebSocketProtocol

    from sugar_odm import MongoDB
    from sugar_api import Redis

    import websocket
    from engine import LifeEngine as LE

    LE.configure(args)

    LE.output.setLevel(INFO)

    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    MongoDB.set_event_loop(loop)
    loop.run_until_complete(Redis.set_event_loop(loop))

    LE.output.info(f'{Fore.GREEN}Starting Life Engine...{Style.RESET_ALL}')
    loop.run_until_complete(LE.run())
    LE.output.info(f'{Fore.GREEN}Stopping Life Engine...{Style.RESET_ALL}')
elif args.command == 'world':
    import signal
    import uvloop, asyncio
    from asyncio import create_task

    from sugar_odm import MongoDB
    from sugar_api import Redis

    from seed import Seed
    from world.cache import WorldCache as WC

    WC.configure(args)

    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    async def main():
        MongoDB.set_event_loop(loop)
        await Redis.set_event_loop(loop)

        WC.init()
        try:
            await WC.inint_monsters()
        except KeyboardInterrupt:
            await WC.remove_monsters()

        while True:
            try:
                input()
            except KeyboardInterrupt:
                await WC.remove_monsters()
                break


    loop.run_until_complete(main())

else:
    parser.print_help()
