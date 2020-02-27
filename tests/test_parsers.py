import json
import math
import os
from BrainStorm import image as im
from BrainStorm import parsers
from BrainStorm.proto import Snapshot


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



def test_translation_parser_registered():
    assert 'pose' in parsers.registered_parsers


def test_col_img_parser_registered():
    assert 'color_image' in parsers.registered_parsers


def test_image_write(tmp_path):
    my_dir = tmp_path / 'my_dir'
    my_dir.mkdir()
    img = im.image('Color',2,2,(b'\xff\x00\x00'
                                b'\x00\xff\x00'
                                b'\x20\x20\x00'
                                b'\x80\x80\xff'))
    snap = Snapshot(0,None,None,img,None,None)
    con = parser_context(my_dir)
    parsers.registered_parsers['color_image'](con,snap)
    expected_file = my_dir / 'color_image.jpg'
    assert expected_file.exists()
    assert expected_file.is_file()

def test_translation_content(tmp_path):
    my_dir = tmp_path / 'my_dir'
    my_dir.mkdir()
    translation = {'x':1.1,'y':2.2,'z':3.3}
    rot = {'x':1.1,'y':2.2,'z':3.3,'w':4.4}
    snap = Snapshot(0,translation,None,None,None,None)
    con = parser_context(my_dir)
    res = parsers.registered_parsers['pose'](con,snap)
    j = res
    assert 'translation' in j
    retr_trans = j['translation']
    assert 'x' in retr_trans
    assert 'y' in retr_trans
    assert 'z' in retr_trans
    for k in retr_trans:
        assert math.isclose(retr_trans[k],translation[k])
