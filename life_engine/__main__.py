import argparse, sys

from colorama import Fore, Back, Style

parser = argparse.ArgumentParser(description='life')
subparsers = parser.add_subparsers(help='command help', dest='command')
api_parser = subparsers.add_parser('api', help='api help')
engine_parser = subparsers.add_parser('engine', help='engine help')
seed_parser = subparsers.add_parser('seed', help='seed help')

engine_parser.add_argument('-c', '--country', required=True)
engine_parser.add_argument('-s', '--state', required=True)
engine_parser.add_argument('-y', '--county', required=True)

if len(sys.argv) == 1:
    parser.print_help()

args = parser.parse_args()

from sugar_api import WebToken

WebToken.set_secret('secret')

if args.command == 'api':
    import resource

    import handlers
    from api import server

    print(f'{Fore.GREEN}Starting Life API Server...{Style.RESET_ALL}')
    server.run(host='127.0.0.1', port='8001')
    print(f'{Fore.GREEN}Stopping Life API Server...{Style.RESET_ALL}')
elif args.command == 'engine':
    from sanic.websocket import WebSocketProtocol

    import websocket
    from engine import LifeEngine as LE
    from world.cache import WorldCache as WC

    WC.configure(args)

    print(f'{Fore.GREEN}Starting Life Engine...{Style.RESET_ALL}')
    LE.server.run(host='127.0.0.1', port='8000', protocol=WebSocketProtocol)
    print(f'{Fore.GREEN}Stopping Life Engine...{Style.RESET_ALL}')
elif args.command == 'seed':
    import uvloop, asyncio

    from seed import Seed

    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(Seed.profiles())
else:
    parser.print_help()
