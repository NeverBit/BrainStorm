import socket
import struct
import time
from .connection import Connection
from .mindreader import reader, Snapshot
from .proto import Hello, Config
from .proto import Snapshot as SnapshotMsg
from .image import image

def make_minimal_snapshot_msg(snap,supported_fields):
    time = snap.timestamp
    trans = snap.translation
    rot = snap.rotation
    col_img = snap.col_img
    dep_img = snap.dep_img
    emo = snap.emotions

    if('translation' not in supported_fields):
        trans = dict.fromkeys(trans, 0) 

    if('rotation' not in supported_fields):
        rot = dict.fromkeys(rot, 0) 

    if('color_image' not in supported_fields):
        col_img = image('Color',0,0,b'')

    if('depth_image' not in supported_fields):
        dep_img = image('Depth',0,0,b'')

    if('emotions' not in supported_fields):
        emo = (0,0,0,0)

    return SnapshotMsg(time,trans,rot,col_img,dep_img,emo)


def upload_thoughts(address,port, sample_file):
    print(' @@@ Debug before reader start ')
    s_reader = reader(sample_file)
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
            print(snap)
            snap_msg = make_minimal_snapshot_msg(snap,conf.supported_fields)
            print(snap_msg)
            con.send_message(snap_msg.serialize())
            print(' @@@ Debug snap sent!')
            pass
        snap = None
    snap = s_reader.read_snapshot()
    print('done')
