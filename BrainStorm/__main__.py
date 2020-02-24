import sys
import client
from .utils import Connection,Listener
from .server import run_server
from .web import run_webserver
import click

@click.group()
def main():
    pass

@main.group('server')
def server():
    pass

@server.command(name='run')
@click.argument('ip',type=str)
@click.argument('port',type=int)
def run_server_command(ip,port):
    data_path = 'data'
    run_server(ip,port,data_path)
    pass

@main.command(name='run_webserver')
def run_webserver_command():
    pass


if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm', obj={})
    except Exception as error:
        print(f'ERROR: {error}')
        sys.exit(1)
