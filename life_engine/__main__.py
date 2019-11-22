import argparse, sys

from colorama import Fore, Back, Style


parser = argparse.ArgumentParser(description='life')
subparsers = parser.add_subparsers(help='command help', dest='command')
api_parser = subparsers.add_parser('api', help='api help')
engine_parser = subparsers.add_parser('engine', help='engine help')


if len(sys.argv) == 1:
    parser.print_help()


args = parser.parse_args()


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

    print(f'{Fore.GREEN}Starting Life Engine...{Style.RESET_ALL}')
    LE.server.run(host='127.0.0.1', port='8000', protocol=WebSocketProtocol)
    print(f'{Fore.GREEN}Stopping Life Engine...{Style.RESET_ALL}')
else:
    parser.print_help()
