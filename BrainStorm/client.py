import socket
import struct
import time
from .connection import Connection
from .mindreader import get_reader
from .proto import Hello, Config
from .proto import Snapshot as SnapshotMsg
from .image import image

def make_minimal_snapshot_msg(snap,supported_fields):
    time = snap.datetime
    trans = snap.pose.translation
    rot = snap.pose.rotation
    col_img = snap.color_image
    dep_img = snap.depth_image
    emo = snap.feelings

    trans = {'x':trans.x,'y':trans.y,'z':trans.z} 
    if('translation' not in supported_fields):
        trans = {'x':0,'y':0,'z':0} 

    rot = {'x':rot.x,'y':rot.y,'z':rot.z,'w':rot.w} 
    if('rotation' not in supported_fields):
        rot = {'x':0,'y':0,'z':0,'w':0} 

    if('color_image' not in supported_fields):
        col_img = image('Color',0,0,b'')

    if('depth_image' not in supported_fields):
        dep_img = image('Depth',0,0,b'')

    if('emotions' not in supported_fields):
        emo = (0,0,0,0)

    return SnapshotMsg(time,trans,rot,col_img,dep_img,emo)


def upload_thoughts(address,port, sample_file):
    print(' @@@ Debug before reader start ')
    reader_class = get_reader(2)
    s_reader = reader_class(sample_file)
    print(' @@@ Debug making hello')
    hello_msg = Hello(s_reader.uid,s_reader.uname,s_reader.bday,s_reader.gender)
    print(' @@@ Debug done making hello')
    snap = s_reader.read_snapshot()
    while snap != None:
        with Connection.connect(address,port) as con:
            print(' @@@ Debug sending message using connection class')
            con.send_message(hello_msg.serialize())
            print(' @@@ Debug sent')
            data = con.receive_message()
            conf = Config.deserialize(data)
            print(conf)
            print(' @@@ Debug got a snap')
            snap_msg = make_minimal_snapshot_msg(snap,conf.supported_fields)
            print(f' @@@ Debug minimalized snap: {snap_msg}')
            con.send_message(snap_msg.serialize())
            print(' @@@ Debug snap sent!')
            pass
        snap = s_reader.read_snapshot()
        time.sleep(5.5)
    print('done')
