import click
from .db_access import Reader
import flask
from .image import image
import importlib
import json
import mimetypes
from . import mq
from . import parsers_store
from . import parsers
from pathlib import Path
import pika
from .proto import Snapshot, SnapshotSlim
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, BigInteger, String, ForeignKey, and_


app = flask.Flask(__name__)
serverInst = None


class WebServer:
    def __init__(self, database_url):
        self.reader = Reader(database_url)

    def home(self):
        ''' Returns the home page '''
        return flask.send_from_directory('static_resources', 'home.html')

    def main_style(self):
        ''' Returns the home page '''
        return flask.send_from_directory('static_resources', 'main.css')

    def logo_file(self, ext):
        ''' Returns one of the logo files (html, css, js) '''
        if ext not in ['html', 'css', 'js']:
            flask.abort(404)
        mimetype = 'text'
        print(mimetypes.guess_type('style.css'))
        return flask.send_from_directory('static_resources', 'logo.' + ext)

    def users(self):
        ''' Returns the home page '''
        users = self.reader.get_users()
        users[99] = "Shappy"
        print(f'users: {users}\r\nType: {type(users)}')
        return flask.render_template('users.html', users=users)


@app.route('/')
def get_home():
    return serverInst.home()


@app.route('/main.css')
def get_main_style():
    return serverInst.main_style()


@app.route('/logo.<ext>')
def get_logo(ext):
    return serverInst.logo_file(ext)


@app.route('/users')
def get_users():
    return serverInst.users()


@click.group()
def main():
    pass


@main.command(name='run-server')
@click.option('-h', '--host', type=str, default='127.0.0.1')
@click.option('-p', '--port', type=str, default=8080)
@click.argument('database_url', type=str)
def run_server(host, port, database_url):
    global serverInst
    serverInst = WebServer(database_url)
    print(f' @@@ Debug run-server and serverInst is {serverInst}')

    # let flask take the reins
    app.run(host=host, port=port, threaded=True)


if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm.gui', obj={})
    except Exception as error:
        print(f'ERROR: {error}')
        sys.exit(1)
