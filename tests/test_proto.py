import struct
from BrainStorm import proto
from BrainStorm import image


TEST_USER_INFO = proto.UserInfo(42, 'Name Name', 10101, 'm')
TEST_DATE_TIME = 2


def test_snapshot_ser_des():
    class dummy_obj:
        pass
    col_img = image(2, 2, b'\xff\x00\x00' * 4)
    dep_img = image(1, 1, struct.pack('!f', 0.75))
    trans = dummy_obj()
    trans.x = 1.1
    trans.y = 2.1
    trans.z = 3.1
    rot = dummy_obj()
    rot.x = 1.1
    rot.y = 2.2
    rot.z = 3.3
    rot.w = 4.4
    feel = dummy_obj()
    feel.hunger = 1.0
    feel.thirst = 0.0
    feel.exhaustion = -1.0
    feel.happiness = 1.0
    s1 = proto.Snapshot(
        TEST_USER_INFO,
        TEST_DATE_TIME,
        trans,
        rot,
        col_img,
        dep_img,
        feel)
    s2 = proto.Snapshot.fromDict(s1.toDict())
    assert repr(s1) == repr(s2)


def test_snapshot_ser_des_with_nones():
    col_img = image(2, 2, b'\xff\x00\x00' * 4)
    dep_img = image(1, 1, struct.pack('!f', 0.75))
    trans = None
    rot = None
    feel = None
    s1 = proto.Snapshot(
        TEST_USER_INFO,
        TEST_DATE_TIME,
        trans,
        rot,
        col_img,
        dep_img,
        feel)
    s2 = proto.Snapshot.fromDict(s1.toDict())
    assert repr(s1) == repr(s2)


def test_snapshotslim_ser_des():
    col_img_path = 'path/to/file'
    dep_img_path = 'path/to/other/file'
    trans = {'x': 1.1, 'y': 2.2, 'z': 3.3}
    rot = {'x': 1.1, 'y': 2.2, 'z': 3.3, 'w': 4.4}
    feel = (1.0, 0.0, -1.0, 1.0)
    s1 = proto.SnapshotSlim(
        TEST_USER_INFO,
        101,
        trans,
        rot,
        col_img_path,
        dep_img_path,
        feel)
    s2 = proto.SnapshotSlim.fromDict(s1.toDict())
    assert repr(s1) == repr(s2)


def test_snapshotslim_ser_des_with_nones():
    col_img_path = 'path/to/file'
    dep_img_path = 'path/to/other/file'
    trans = None
    rot = None
    feel = None
    s1 = proto.SnapshotSlim(
        TEST_USER_INFO,
        101,
        trans,
        rot,
        col_img_path,
        dep_img_path,
        feel)
    s2 = proto.SnapshotSlim.fromDict(s1.toDict())
    assert repr(s1) == repr(s2)
