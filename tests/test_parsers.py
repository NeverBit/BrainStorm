import bson
import json
import math
import os
from pathlib import Path
from BrainStorm import image as im
from BrainStorm import parsers
from BrainStorm.proto import Snapshot
from BrainStorm.proto import SnapshotSlim

TEST_USER_ID = 1
TEST_DATE_TIME = 2

class parser_context:
    def __init__(self,save_dir):
        self.dir = save_dir
        self.save_call_count = 0
        self.get_encoded_image_count = 0
        self.get_storage_path_count = 0
    def get_storage_path(self):
        self.get_storage_path_count += 1
        return self.dir
    def save(self,filename,data):
        self.save_call_count += 1
        filepath = self.dir / filename
        with filepath.open('w') as f:
            f.write(data)
        print(f' @@@ DEBUG Saved {len(data)} bytes to {filepath}')
    def set_encoded_image_to_return(self,img):
        self.enc_img = img
    def get_encoded_image(self,path):
        return self.enc_img


def test_translation_parser_registered():
    assert 'pose' in parsers.registered_parsers


def test_col_img_parser_registered():
    assert 'color_image' in parsers.registered_parsers


def test__color_image__write(tmp_path):
    my_dir = tmp_path / 'my_dir'
    my_dir.mkdir()
    img = im.image(2,2,(b'\xff\x00\x00'
                                b'\x00\xff\x00'
                                b'\x20\x20\x00'
                                b'\x80\x80\xff'))
    img_path = my_dir / 'image.bin'

    snap = SnapshotSlim(TEST_USER_ID,TEST_DATE_TIME,None,None,img_path,None,None)
    con = parser_context(my_dir)
    con.set_encoded_image_to_return(img)
    parser = parsers.registered_parsers['color_image']
    res = parser(con,snap)
    assert res != None
    assert res['path'] != None
    assert Path(res['path']).is_file()


def test__color_image__get_encoded_image_called(tmp_path):
    my_dir = tmp_path / 'my_dir'
    my_dir.mkdir()
    img = im.image(2,2,(b'\xff\x00\x00'
                                b'\x00\xff\x00'
                                b'\x20\x20\x00'
                                b'\x80\x80\xff'))
    img_path = my_dir / 'image.bin'

    snap = SnapshotSlim(TEST_USER_ID,TEST_DATE_TIME,None,None,img_path,None,None)
    con = parser_context(my_dir)
    con.set_encoded_image_to_return(img)
    parser = parsers.registered_parsers['color_image']
    res = parser(con,snap)
    assert con.get_encoded_image != 0


def test__color_image__get_encoded_image_called(tmp_path):
    my_dir = tmp_path / 'my_dir'
    my_dir.mkdir()
    img = im.image(2,2,(b'\xff\x00\x00'
                                b'\x00\xff\x00'
                                b'\x20\x20\x00'
                                b'\x80\x80\xff'))
    img_path = my_dir / 'image.bin'

    snap = SnapshotSlim(TEST_USER_ID,TEST_DATE_TIME,None,None,img_path,None,None)
    con = parser_context(my_dir)
    con.set_encoded_image_to_return(img)
    parser = parsers.registered_parsers['color_image']
    res = parser(con,snap)
    assert con.get_encoded_image != 0


def test__color_image__get_encoded_image_called(tmp_path):
    my_dir = tmp_path / 'my_dir'
    my_dir.mkdir()
    img = im.image(2,2,(b'\xff\x00\x00'
                                b'\x00\xff\x00'
                                b'\x20\x20\x00'
                                b'\x80\x80\xff'))
    img_path = my_dir / 'image.bin'

    snap = SnapshotSlim(TEST_USER_ID,TEST_DATE_TIME,None,None,img_path,None,None)
    con = parser_context(my_dir)
    con.set_encoded_image_to_return(img)
    parser = parsers.registered_parsers['color_image']
    res = parser(con,snap)
    assert con.get_encoded_image != 0

def test_translation_content(tmp_path):
    my_dir = tmp_path / 'my_dir'
    my_dir.mkdir()
    translation = {'x':1.1,'y':2.2,'z':3.3}
    rot = {'x':1.1,'y':2.2,'z':3.3,'w':4.4}
    snap = SnapshotSlim(TEST_USER_ID,TEST_DATE_TIME,translation,None,None,None,None)
    con = parser_context(my_dir)
    res = parsers.registered_parsers['pose'](con,snap)
    j = json.loads(res)
    assert 'translation' in j
    retr_trans = j['translation']
    assert 'x' in retr_trans
    assert 'y' in retr_trans
    assert 'z' in retr_trans
    for k in retr_trans:
        assert math.isclose(retr_trans[k],translation[k])
