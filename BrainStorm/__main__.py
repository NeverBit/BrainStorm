import sys
from .thought import Thought
from .utils import Connection,Listener
from .server import run_server
from .client import upload_thoughts
from .web import run_webserver
import click

@click.group()
def main():
    pass

@main.group('server')
def server():
    pass

@main.group('client')
def client():
    pass

@client.command(name='run')
@click.argument('sample_path',type=str)
@click.argument('ip',type=str)
@click.argument('port',type=int)
def upload_thought_command(sample_path,ip,port):
    print(' @@@ Debug inside main handler')
    with open(sample_path,'rb') as fd:
        upload_thoughts(ip,port,fd)
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
