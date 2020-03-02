import bson
import click
import gzip
import json
import requests
import socket
import struct
import sys
import time
from .image import image
from .mindreader import get_reader
from .proto import Snapshot

def make_minimal_snapshot_msg(snap,supported_fields):
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

    trans = {'x':trans.x,'y':trans.y,'z':trans.z} 
    rot = {'x':rot.x,'y':rot.y,'z':rot.z,'w':rot.w} 
    if('pose' not in supported_fields):
        trans = {'x':0,'y':0,'z':0} 
        rot = {'x':0,'y':0,'z':0,'w':0} 

    if('color_image' not in supported_fields):
        col_img = image(0,0,b'')

    if('depth_image' not in supported_fields):
        dep_img = image(0,0,b'')

    if('feelings' not in supported_fields):
        feel = (0,0,0,0)

    return Snapshot(uid,dtime,trans,rot,col_img,dep_img,feel)


@click.group()
def main():
    pass

@main.command(name='upload-sample')
@click.option('-h', '--host', type=str, default='127.0.0.1')
@click.option('-p', '--port', type=str, default=8000)
@click.argument('file', type=click.File('rb'))
def upload_sample_file(host, port, file):
    base_url = f'http://{host}:{port}'
    print(' @@@ Debug before reader start ')
    reader_class = get_reader(versionNum=2)
    if(file.name.endswith('gz')):
        file.seek(0)
        file = gzip.GzipFile(fileobj=file)
    s_reader = reader_class(file)
    with requests.Session() as s:
        print(' @@@ Debug making hello')
        hello_msg = {'uid':s_reader.uid,
                    'username':s_reader.uname,
                    'birthday':s_reader.bday,
                    'gender':s_reader.gender}
        print(f'Hello Msg: {hello_msg}')
        print(f'cookies: {s.cookies.get_dict()}')
        hello_response = s.post(f'{base_url}/hello',json=hello_msg)
        print(hello_response)
        print(f'cookies: {s.cookies.get_dict()}')
        for x in requests.session().cookies:
            print(f'a cookie!: {x}')
        conf_response = s.get(f'{base_url}/config')
        supported_fields = json.loads(conf_response.content)
        print(conf_response)
        print(conf_response.content)
        print(supported_fields)
        # Start reading snapshots
        snap = s_reader.read_snapshot()
        while snap != None:
            print(' @@@ Debug got a snap')
            snap_msg = make_minimal_snapshot_msg(snap,supported_fields)
            print(' @@@ Debug dictting snap')
            snapshot_dict = snap_msg.toDict()
            snapshot_bson = bson.dumps(snapshot_dict)    
            print(f'bson\'d!')
            headers = {'Content-type': 'application/bson'}
            snap_response = s.post(f'{base_url}/snapshot',
                                    data=snapshot_bson,
                                    headers=headers)
            print(f' @@@ Debug snap sent! Response: {snap_response}')
            snap = s_reader.read_snapshot()
    print('done')


def upload_sample(host, port, path):
    with open(path,'rb') as file:
        upload_sample_file(host,port,file)



if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm.client', obj={})
    except Exception as error:
        print(f'ERROR: {error}')
        sys.exit(1)
