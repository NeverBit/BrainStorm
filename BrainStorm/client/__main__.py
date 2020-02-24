import sys
import client
from .utils import Connection,Listener
from .server import run_server
from .client import upload_sample
from .web import run_webserver
import click

@click.group()
def main():
    pass

@main.command(name='upload_sample')
@click.argument('host',type=str)
@click.argument('port',type=int)
@click.argument('sample_path',type=str)
def upload_thought_command(ip, port, sample_path):
    print(' @@@ Debug inside CLIENT upload sample handler')
    with open(sample_path,'rb') as fd:
        upload_sample(ip,port,fd)
    pass

if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm', obj={})
    except Exception as error:
        print(f'ERROR: {error}')
        sys.exit(1)
