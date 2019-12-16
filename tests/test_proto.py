import struct
from BrainStorm import proto
from BrainStorm import image as im


def test_hello_ser_des():
    h = proto.Hello(1234,"Hello World",5678,'m')
    h2 = proto.Hello.deserialize(h.serialize())
    assert repr(h) == repr(h2)


def test_config_ser_des():
    h = proto.Config(['aaa','b','cccc','dd'])
    h2 = proto.Config.deserialize(h.serialize())
    assert repr(h) == repr(h2)


def test_snapshot_ser_des():
    col_img = im.image('Color',2,2,b'\xff\x00\x00'*4)
    dep_img = im.image('Depth',1,1,struct.pack('!f',0.75))
    trans = {'x':1.1,'y':2.2,'z':3.3}
    rot = {'x':1.1,'y':2.2,'z':3.3,'w':4.4}
    feel = (1.0,0.0,-1.0,1.0)
    s1 = proto.Snapshot(101,trans,rot,col_img,dep_img,feel)
    s2 = proto.Snapshot.deserialize(s1.serialize())
    assert repr(s1) == repr(s2)
