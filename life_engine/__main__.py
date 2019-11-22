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

    from api import server

    print(f'{Fore.GREEN}Starting Life API Server...{Style.RESET_ALL}')
    server.run(host='127.0.0.1', port='8000')
    print(f'{Fore.GREEN}Stopping Life API Server...{Style.RESET_ALL}')
elif args.command == 'engine':
    from engine import LifeEngine

    print(f'{Fore.GREEN}Starting Life Engine...{Style.RESET_ALL}')
    LifeEngine.server.run()
    print(f'{Fore.GREEN}Stopping Life Engine...{Style.RESET_ALL}')
else:
    parser.print_help()
