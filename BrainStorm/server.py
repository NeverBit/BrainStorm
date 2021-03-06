import base64
import bson
import click
import flask
import json
from pathlib import Path
import sys
import threading
from . import mq
from .proto import Snapshot, SnapshotSlim, UserInfo
from . import parsers
import tempfile
import traceback


app = flask.Flask(__name__)
serverInst = None
BRAINSTORM_COOKIE = 'bs-user'


class SnapshotsServer:
    ''' Class to handle all clients' connections '''
    def __init__(self, data_dir, publish):
        self.data_dir = data_dir
        self.files_lock = threading.Lock()
        self.publish = publish

    def client_hello(self):
        ''' Handle Hello messages from the clients '''
        try:
            req = flask.request.json
            resp = flask.make_response()
            enc_json = json.dumps(req).encode()
            resp.set_cookie(BRAINSTORM_COOKIE, base64.b64encode(enc_json))
            return resp
        except Exception as error:
            print(f'Error while processing hello : {error}')
            return flask.abort(500)

    def server_config(self):
        ''' Handle Config messages from the clients '''
        parsers_names = list(parsers.registered_parsers.keys())
        return flask.jsonify(parsers_names)

    def save_image(self, path, img):
        '''
        Saves an image from the snapshot to a path
        (in the blob store)
        '''
        img_bson = bson.dumps(img.toDict())
        with open(path, 'wb') as f:
            f.write(img_bson)

    def client_snapshot(self):
        # Get user info from cookie
        if BRAINSTORM_COOKIE not in flask.request.cookies:
            print('Cookie missing in snapshot request, dropping!')
            return flask.abort(
                400, 'Cookie missing from request. Call /hello first')
        user_cookie = base64.b64decode(
            flask.request.cookies[BRAINSTORM_COOKIE])
        user_info = UserInfo.fromDict(json.loads(user_cookie.decode()))
        # Get snapshot from request data
        snapshot_bson = flask.request.data
        snapshot_dict = bson.loads(snapshot_bson)
        snapshot = Snapshot.fromDict(snapshot_dict)
        datetime = snapshot.datetime
        
        # Make user & time directories
        dd_path = Path(self.data_dir)
        dd_path.mkdir(exist_ok=True)
        user_path = dd_path / f'{user_info.uid}'
        user_path.mkdir(exist_ok=True)
        datetime_path = user_path / f'{datetime}'
        datetime_path.mkdir(exist_ok=True)
        # Save images to filesystem
        col_img_path = datetime_path / f'color_image.bson'
        self.save_image(col_img_path, snapshot.col_img)
        dep_img_path = datetime_path / f'depth_image.bson'
        self.save_image(dep_img_path, snapshot.dep_img)

        # Make Slim snapshot (with the images paths)
        slimshot = SnapshotSlim(user_info,
                                datetime,
                                snapshot.pose.translation,
                                snapshot.pose.rotation,
                                str(col_img_path),
                                str(dep_img_path),
                                snapshot.feelings)

        # Publish to MQ
        slim_json = json.dumps(slimshot.toDict())
        self.publish(slim_json)

        return flask.Response(status=200)


@app.route('/hello', methods=['POST'])
def client_hello():
    ''' Handle Hello messages from the clients '''
    return serverInst.client_hello()


@app.route('/config')
def server_config():
    ''' Handle Config messages from the clients '''
    return serverInst.server_config()


@app.route('/snapshot', methods=['POST'])
def client_snapshot():
    ''' Handle new Snapshots from the clients '''
    return serverInst.client_snapshot()


def run_server(host, port, publish, data_dir=None):
    ''' Runs the server, expecting new clients connections'''
    if data_dir == None:
        path_obj = Path(tempfile.gettempdir()) / 'brainstorm' / 'data'
        data_dir = str(path_obj)
        if not path_obj.exists():
            os.makedirs(data_dir)
    global serverInst
    serverInst = SnapshotsServer(data_dir, publish)
    # let flask take the reins
    app.run(host=host, port=port, threaded=True)


@click.group()
def main():
    pass


@main.command(name='run-server')
@click.option('-h', '--host', type=str, default='127.0.0.1')
@click.option('-p', '--port', type=str, default=8000)
@click.argument('mq_con_string', type=str)
def run_server_mq(host, port, mq_con_string):
    '''
    Runs the server and publishes the 
    snapshots received from the clients to an MQ topic
    '''
    mq_con = mq.create_mq_connection(mq_con_string, 'input')

    def mq_publish(msg):
        mq_con.open()
        mq_con.publish(msg)
        mq_con.close()
    publish = mq_publish
    run_server(host, port, publish)


if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm.server', obj={})
    except Exception as error:
        print(f'ERROR: {error}')
        sys.exit(1)
