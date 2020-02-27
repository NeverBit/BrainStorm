import click
import importlib
import json
from . import mq
from . import parsers_store
from pathlib import Path
import pika
from .proto import Snapshot
from .proto import SnapshotSlim
import sys


registered_parsers = parsers_store.registered_parsers


# TODO: Move elsewhere
class parser_context:
    def __init__(self,save_dir):
        self.dir = save_dir
    def get_storage_path(self):
        return self.dir
    def save(self,filename,data):
        filepath = self.dir / filename
        with filepath.open('w') as f:
            f.write(data)
        print(f' @@@ DEBUG Saved {len(data)} bytes to {filepath}')


@click.group()
def main():
    pass


@main.command(name='parse')
@click.argument('name', type=str)
@click.argument('input', type=click.File('r'))
def run_parser_once(name,input):
    print(' @@@ Debug in run_parser_once')
    # Resolve parser name to function
    parse_func = registered_parsers[name]

    # Parse input snapshot
    print(' @@@ Debug fromDict')
    snapshot = SnapshotSlim.fromDict(json.loads(input.read()))
    print(' @@@ Debug in parsing')
    context = parser_context(Path('resources'))
    res = parse_func(context,snapshot)
    print(' @@@ Debug in done parsing')
    json_snap = json.dumps(res)
    print(json_snap)


@main.command(name='run-parser')
@click.argument('name', type=str)
@click.argument('connection_string', type=str)
def run_parser_service(name,connection_string):
    # Resolve parser name to function
    parse_func = registered_parsers[name]

    # Create MQ connection towards saver
    con_to_saver = mq.create_mq_connection(connection_string, 'save')

    # Define parse & publish callback
    def callback(channel, method, properties, body):
        snapshot = SnapshotSlim.fromDict(json.loads(body))
        context = parser_context('resources')
        res = parse_func(context,snapshot)
        json_snap = json.dumps(res)
        con_to_saver.publish(json_snap)

    # Consume input mq
    con_to_input = mq.create_mq_connection(connection_string, 'input')
    con_to_input.start_consume(callback)


if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm.parsers', obj={})
    except Exception as error:
        print(error)
        print(f'ERROR: {error}')
        sys.exit(1)
