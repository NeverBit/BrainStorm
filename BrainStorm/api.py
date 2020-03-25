import click
from .db_access import Reader
import flask
import json
import os
from pathlib import Path
import pika
from .proto import Snapshot, SnapshotSlim, UserInfo
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey, and_
import traceback


app = flask.Flask(__name__)
readerInst = None


@app.route('/users')
def get_users_list():
    return readerInst.get_users()


@app.route('/users/<int:user_id>')
def get_user(user_id):
    user = readerInst.get_user(user_id)
    if user:
        return user
    flask.abort(404)


@app.route('/users/<int:user_id>/snapshots')
def get_user_snapshots_list(user_id):
    if not readerInst.get_user(user_id):
        flask.abort(404)
    return readerInst.get_snapshots_by_user(user_id)


@app.route('/users/<int:user_id>/snapshots/<int:snapshot_id>')
def get_snapshot(user_id, snapshot_id):
    print('get_snapshot(user_id, snapshot_id):')
    snapshot = readerInst.get_snapshot(user_id, snapshot_id)
    if snapshot:
        return snapshot
    flask.abort(404)


@app.route(
    '/users/<int:user_id>/snapshots/<int:snapshot_id>/<result_name>',
    methods=['GET'])
def get_result(user_id, snapshot_id, result_name):
    results = readerInst.get_parser_res(result_name, snapshot_id)
    if results:
        return results
    flask.abort(404)


def get_content_type_by_ext(path):
    ''' Returns an HTTP content type based on the extension of a file '''
    _, file_extension = os.path.splitext(path)
    if(file_extension == '.jpg' or file_extension == '.jpeg'):
        return 'image/jpeg'
    # Add more cases to support more formats

    # Fallback if we did't find the right type
    return 'application/octet-stream'


@app.route(
    '/users/<int:user_id>/snapshots/<int:snapshot_id>/<result_name>/data',
    methods=['GET'])
def get_result_data(user_id, snapshot_id, result_name):
    results = readerInst.get_parser_res(result_name, snapshot_id)
    if not results:
        # Could not find specific result/snapshot
        flask.abort(404)

    res_dict = json.loads(results)
    if 'data_path' not in res_dict:
        # The specific result type does indicate raw data is available
        flask.abort(404)

    path = res_dict['data_path']
    with open(path, 'rb') as f:
        result_data = f.read()

    content_type = get_content_type_by_ext(path)
    return flask.Response(result_data, mimetype=content_type)


@click.group()
def main():
    pass


@main.command(name='run-server')
@click.option('-h', '--host', type=str, default='127.0.0.1')
@click.option('-p', '--port', type=str, default=5000)
@click.argument('database_url', type=str)
def run_api_server(host, port, database_url):
    global readerInst
    readerInst = Reader(database_url)
    app.run(host=host, port=port, threaded=True)


if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm.api', obj={})
    except Exception as error:
        print(f'ERROR: {error}')
        track = traceback.format_exc()
        print(track)
        sys.exit(1)
