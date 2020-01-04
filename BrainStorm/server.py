import base64
import bson
import json
from pathlib import Path
import socket
import struct
import time
import threading
import flask
from .connection import Connection
from .proto import Snapshot
from . import parsers
from . import proto


app = flask.Flask(__name__)

data_dir = None
files_lock = threading.Lock()

parsers_list = parsers.registered_parsers
parsers_names = list(parsers_list.keys())
BRAINSTORM_COOKIE = 'bs-user'


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


@app.route('/hello', methods = ['POST'])
def client_hello():
    try:
        req = flask.request.json
        resp = flask.make_response()
        enc_json = json.dumps(req).encode()
        print('Returning hello request with set cookie!')
        resp.set_cookie(BRAINSTORM_COOKIE, base64.b64encode(enc_json))
        return resp
    except Exception as error:
        print(f'Error in /hello : {error}')
        return flask.abort(500)


@app.route('/config', methods = ['GET'])
def server_config():
    return flask.jsonify(parsers_names)


@app.route('/snapshot', methods = ['POST'])
def client_snapshot():
    if BRAINSTORM_COOKIE not in flask.request.cookies:
        print('Cookie missing in snapshot request, dropping!')
        return flask.abort(400,'Cookie missing from request. Call /hello first')
    user_cookie = base64.b64decode(flask.request.cookies[BRAINSTORM_COOKIE])
    snapshot_bson = flask.request.data
    snapshot_dict = bson.loads(snapshot_bson)
    snapshot = Snapshot.fromDict(snapshot_dict)
    timestamp = snapshot.timestamp
    user_info = json.loads(user_cookie.decode())
    uid = user_info['uid']
    print(f'user info  {user_info} sent snapshot : {timestamp}')

    # Make user & time directories
    dd_path = Path(data_dir)
    dd_path.mkdir(exist_ok=True)
    user_path = dd_path / f'{uid}'
    user_path.mkdir(exist_ok=True)
    datetime_path = user_path / f'{timestamp}'
    datetime_path.mkdir(exist_ok=True)
    print('It\'s OK')

    # Create context for parsers
    p_context = parser_context(datetime_path)
    # Run parsers
    for parser in parsers_list.values():
        parser(p_context,snapshot)   

    return flask.Response(status=200)


def run_server(address,port,data_dirr):
    global data_dir
    data_dir = data_dirr
    # let flask take the the reins
    app.run(host=address,port=port)
