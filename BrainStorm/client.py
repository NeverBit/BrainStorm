import bson
import click
import json
import requests
import socket
import struct
import time
from .connection import Connection
from .image import image
from .mindreader import get_reader
from .proto import Snapshot

def make_minimal_snapshot_msg(snap,supported_fields):
    time = snap.datetime
    trans = snap.pose.translation
    rot = snap.pose.rotation
    col_img = snap.color_image
    dep_img = snap.depth_image
    emo = snap.feelings

    trans = {'x':trans.x,'y':trans.y,'z':trans.z} 
    rot = {'x':rot.x,'y':rot.y,'z':rot.z,'w':rot.w} 
    if('pose' not in supported_fields):
        trans = {'x':0,'y':0,'z':0} 
        rot = {'x':0,'y':0,'z':0,'w':0} 

    col_img = image('Color',col_img.height,col_img.width,col_img.data)
    if('color_image' not in supported_fields):
        col_img = image('Color',0,0,b'')

    dep_img = image('depth',dep_img.height,dep_img.width,dep_img.data)
    if('depth_image' not in supported_fields):
        dep_img = image('Depth',0,0,b'')

    if('emotions' not in supported_fields):
        emo = (0,0,0,0)

    return Snapshot(time,trans,rot,col_img,dep_img,emo)

@click.group()
def main():
    pass

def upload_sample(host, port, path):
    with open(path,'rb') as file:
        upload_sample_file(host,port,file)

@main.command(name='upload-sample')
@click.option('-h', '--host', type=str, default='127.0.0.1')
@click.option('-p', '--port', type=str, default=8000)
@click.argument('file', type=click.File('rb'))
def upload_sample_file(host, port, file):
    base_url = f'http://{host}:{port}'
    print(' @@@ Debug before reader start ')
    reader_class = get_reader(2)
    s_reader = reader_class(path)
    with requests.Session() as s:
        print(' @@@ Debug making hello')
        hello_msg = {'uid':s_reader.uid,
                    'username':s_reader.uname,
                    'birthday':s_reader.bday,
                    'gender':s_reader.gender}
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
            snapshot_dict = snap_msg.toDict()
            snapshot_bson = bson.dumps(snapshot_dict)
            print(f'bson\'d!')
            headers = {'Content-type': 'application/bson'}
            snap_response = s.post(f'{base_url}/snapshot',
                                    data=snapshot_bson,
                                    headers=headers)
            print(f' @@@ Debug snap sent! Response: {snap_response}')
            snap = s_reader.read_snapshot()
            time.sleep(5.5)
    print('done')




if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm.Client', obj={})
    except Exception as error:
        print(f'ERROR: {error}')
        sys.exit(1)
