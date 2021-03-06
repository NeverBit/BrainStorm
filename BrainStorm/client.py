import bson
import click
import gzip
import json
import requests
import sys
from .image import image
from .mindreader import get_reader
from .proto import Snapshot, UserInfo
import traceback


def trim_snapshot(snap, supported_fields):
    '''
    Makes a subset version of a snapshot - containing
    values only for the fields supported by the server
    '''
    uid = snap.uid
    dtime = snap.datetime
    trans = snap.pose.translation
    rot = snap.pose.rotation
    col_img = snap.col_img
    dep_img = snap.dep_img
    feel = snap.feelings

    trans = {'x': trans.x, 'y': trans.y, 'z': trans.z}
    rot = {'x': rot.x, 'y': rot.y, 'z': rot.z, 'w': rot.w}
    if('pose' not in supported_fields):
        trans = {'x': 0, 'y': 0, 'z': 0}
        rot = {'x': 0, 'y': 0, 'z': 0, 'w': 0}

    if('color_image' not in supported_fields):
        col_img = image(0, 0, b'')

    if('depth_image' not in supported_fields):
        dep_img = image(0, 0, b'')

    feel = {'hunger': feel.hunger,
            'thirst': feel.thirst,
            'exhaustion': feel.exhaustion,
            'happiness': feel.happiness,
            }
    if('feelings' not in supported_fields):
        feel = (0, 0, 0, 0)
    return Snapshot(uid, dtime, trans, rot, col_img, dep_img, feel)


def get_http_session():
    '''
    Returns a HTTP session object.
    Decoupled from upload_sample_file for testing purposes
    '''
    return requests.Session()


@click.group()
def main():
    pass


def upload_sample(host, port, path):
    # Open file
    if(path.endswith('gz')):
        file = gzip.GzipFile(path)
    else:
        file = open(path, 'rb')

    base_url = f'http://{host}:{port}'
    reader_class = get_reader(versionNum=2)
    s_reader = reader_class(file)
    with get_http_session() as sess:
        print('Sending Hello to server... ')
        user_info = UserInfo(
            s_reader.uid,
            s_reader.uname,
            s_reader.bday,
            s_reader.gender)
        hello_msg = user_info.toDict()
        # Sending Hello in hopes of getting a cookie 'token'
        # for the rest of the session
        # note: The cookie is automaticlly saved in the
        # 'http session'
        sess.post(f'{base_url}/hello', json=hello_msg)
        print('Got Hello response.')

        print('Sending Config request to server...')
        conf_response = sess.get(f'{base_url}/config')
        supported_fields = json.loads(conf_response.content)
        print('Got Config response.')
        
        # Start reading snapshots
        snap = s_reader.read_snapshot()
        count = 0
        while snap is not None:
            print('Read new snapshot from file')
            snap_msg = trim_snapshot(snap, supported_fields)
            snapshot_dict = snap_msg.toDict()
            snapshot_bson = bson.dumps(snapshot_dict)
            headers = {'Content-type': 'application/bson'}
            print(f'Sending Snapshot #{count} to server...')
            snap_response = sess.post(f'{base_url}/snapshot',
                                      data=snapshot_bson,
                                      headers=headers)
            if(snap_response.status_code != 200):
                print((f'Server rejected the snapshot, '
                      'status code: {snap_response.status_code}.'
                      ' Aborting'))
                break
            print(f'Server accepted the snapshot!')
            snap = s_reader.read_snapshot()
            count += 1
        else:
            print('Done reading input file')


@main.command(name='upload-sample')
@click.option('-h', '--host', type=str, default='127.0.0.1')
@click.option('-p', '--port', type=int, default=8000)
@click.argument('path', type=str)
def upload_sample_cli(host, port, path):
    upload_sample(host, port, path)


if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm.client', obj={})
    except Exception as error:
        print(f'ERROR: {error}')
        sys.exit(1)
