import bson
import click
from .image import image
import json
from . import mq
import os
from .parsers_store import registered_parsers
from pathlib import Path
from .proto import SnapshotSlim
import sys
import tempfile
import traceback


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

def run_parser(name, data):
    # Resolve parser name to function
    if name not in registered_parsers:
        click.echo('No such parser!')
        return
    parse_func = registered_parsers[name]

    # Parse input snapshot
    data_dict = json.loads(data)
    snapshot = SnapshotSlim.fromDict(data_dict)

    # Make parser context
    res_path = Path(tempfile.gettempdir()) / 'brainstorm' / 'resources'
    if not res_path.exists():
        os.makedirs(str(res_path))
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
    return json.dumps(saver_msg)
    

@main.command(name='parse')
@click.argument('name', type=str)
@click.argument('input', type=click.File('r'))
def run_parser_once(name, input):
    # Forward request to run_parser
    res = run_parser(name, input.read())
    click.echo(res)


@main.command(name='run-parser')
@click.argument('name', type=str)
@click.argument('connection_string', type=str)
def run_parser_service(name, connection_string):
    # Resolve parser name to function
    if name not in registered_parsers:
        click.echo('No such parser!')
        return
    parse_func = registered_parsers[name]

    # Create MQ connection towards saver
    try:
        con_to_saver = mq.create_mq_connection(connection_string, 'parsers')
    except Exception as e:
        raise Exception('Failed to connect to MQ. Cannot proceed.')

    # Define parse & publish callback
    def callback(channel, method, properties, body):
        snapshot = SnapshotSlim.fromDict(json.loads(body))
        res_path = Path('/tmp/brainstorm/resources')
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
        con_to_saver.open()
        con_to_saver.publish(saver_msg_json, topic=name)
        con_to_saver.close()

    # Consume input mq
    
    try:
        con_to_input = mq.create_mq_connection(connection_string, 'input')
    except Exception as e:
        raise Exception('Failed to connect to MQ. Cannot proceed.')
    
    try:
        con_to_input.open()
        con_to_input.start_consume(callback)
    except Exception as e:
        raise Exception('MQ error occurred when consuming input queue. Cannot proceed')


if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm.parsers', obj={})
    except Exception as error:
        print(f'ERROR: {error}')
        sys.exit(1)
