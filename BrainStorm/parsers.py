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


registered_parsers = parsers_store.registered_parsers


class parser_context:
    def __init__(self, storage_dir):
        self.dir = storage_dir
    def get_storage_path(self):
        return self.dir
    def get_encoded_image(self,path):
        with open(path, 'rb') as f:
            return image.fromDict(bson.loads(f.read()))


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
    # Make parser context
    res_path = Path('resources')
    res_path.mkdir(exist_ok=True)
    context = parser_context(res_path)
    print(' @@@ Debug parser context made')
    parser_results = parse_func(context,snapshot)
    # Wrap the parer results in a unified format for the server
    saver_msg = {
        'uid':snapshot.uid,
        'datetime':snapshot.datetime,
        'parser_name':name,
        'parser_res':parser_results
    }
    saver_msg_json = json.dumps(saver_msg)
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
    print(f' @@@ Debug Creating MQ connection PARSERS')
    con_to_saver = mq.create_mq_connection(connection_string, 'parsers')
    print(f' @@@ Debug Opening MQ connection')
    con_to_saver.open()
    print(f' @@@ Debug Opened MQ connection')

    # Define parse & publish callback
    def callback(channel, method, properties, body):
        snapshot = SnapshotSlim.fromDict(json.loads(body))
        context = parser_context(Path('resources'))
        parser_results = parse_func(context,snapshot)
        # Wrap the parer results in a unified format for the server
        saver_msg = {
            'uid':snapshot.uid,
            'datetime':snapshot.datetime,
            'parser_name':name,
            'parser_res':parser_results
        }
        saver_msg_json = json.dumps(saver_msg)
        con_to_saver.publish(saver_msg_json, topic=name)

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
        sys.exit(1)
 