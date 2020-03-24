import bson
import click
from .image import image
import importlib
import json
from . import mq
from . import parsers_store
from pathlib import Path
import pika
from .proto import Snapshot
from .proto import SnapshotSlim
import sys
import traceback


registered_parsers = parsers_store.registered_parsers


class parser_context:
    def __init__(self, storage_dir):
        self.dir = storage_dir

    def get_storage_path(self):
        return self.dir

    def get_encoded_image(self, path):
        with open(path, 'rb') as f:
            return image.fromDict(bson.loads(f.read()))


@click.group()
def main():
    pass


@main.command(name='parse')
@click.argument('name', type=str)
@click.argument('input', type=click.File('r'))
def run_parser_once(name, input):
    # Resolve parser name to function
    parse_func = registered_parsers[name]

    # Parse input snapshot
    input_json = json.loads(input.read())
    snapshot = SnapshotSlim.fromDict(input_json)

    # Make parser context
    res_path = Path('resources')
    print('Trying to create resources dir')
    res_path.mkdir(exist_ok=True)
    print('Created(?) resources dir')
    context = parser_context(res_path)
    parser_results = parse_func(context, snapshot)
    # Wrap the parer results in a unified format for the server
    saver_msg = {
        'user_info': snapshot.user_info.toDict(),
        'datetime': snapshot.datetime,
        'parser_name': name,
        'parser_res': parser_results
    }
    saver_msg_json = json.dumps(saver_msg)
    click.echo(saver_msg_json)


@main.command(name='run-parser')
@click.argument('name', type=str)
@click.argument('connection_string', type=str)
def run_parser_service(name, connection_string):
    # Resolve parser name to function
    parse_func = registered_parsers[name]
    print(f' @@@ Running parser "{name}" as a service')

    # Create MQ connection towards saver
    con_to_saver = mq.create_mq_connection(connection_string, 'parsers')

    # Define parse & publish callback
    def callback(channel, method, properties, body):
        snapshot = SnapshotSlim.fromDict(json.loads(body))
        res_path = Path('resources')
        res_path.mkdir(exist_ok=True)
        context = parser_context(res_path)
        parser_results = parse_func(context, snapshot)
        # Wrap the parer results in a unified format for the server
        saver_msg = {
            'user_info': snapshot.user_info.toDict(),
            'datetime': snapshot.datetime,
            'parser_name': name,
            'parser_res': parser_results
        }
        saver_msg_json = json.dumps(saver_msg)
        print(f' @@@ Debug Opening MQ connection')
        con_to_saver.open()
        print(f' @@@ Debug Opened MQ connection')
        con_to_saver.publish(saver_msg_json, topic=name)
        print(f' @@@ Debug Closing MQ connection')
        con_to_saver.close()
        print(f' @@@ Debug Closed MQ connection')

    # Consume input mq
    print(f' @@@ Debug Creating MQ connection input')
    con_to_input = mq.create_mq_connection(connection_string, 'input')
    print(' @@@ Debug Opening MQ connection')
    con_to_input.open()
    print(' @@@ Debug Opened MQ connection')
    con_to_input.start_consume(callback)
    print(' @@@ Debug start_consume MQ connection')


if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm.parsers', obj={})
    except Exception as error:
        print(error)
        print(f'ERROR: {error}')
        track = traceback.format_exc()
        print(track)
        sys.exit(1)
