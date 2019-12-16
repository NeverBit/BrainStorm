import json
import math
import os
from BrainStorm import image as im
from BrainStorm import parsers

class parser_context:
    def __init__(self,directory):
        self.dir = directory


def test_translation_parser_registered():
    assert 'translation' in parsers.registered_parsers


def test_col_img_parser_registered():
    assert 'color_image' in parsers.registered_parsers


def test_image_write(tmp_path):
    my_dir = tmp_path / 'my_dir'
    my_dir.mkdir()
    img = im.image('Color',2,2,(b'\xff\x00\x00'
                                b'\x00\xff\x00'
                                b'\x20\x20\x00'
                                b'\x80\x80\xff'))
    con = parser_context(my_dir)
    parsers.col_img_parser(con,img)
    expected_file = my_dir / 'color_image.jpg'
    assert expected_file.exists()
    assert expected_file.is_file()


def test_translation_write(tmp_path):
    my_dir = tmp_path / 'my_dir'
    my_dir.mkdir()
    translation = {'x':1.1,'y':2.2,'z':3.3}
    con = parser_context(my_dir)
    parsers.trans_parser(con,translation)
    expected_file = my_dir / 'translation.json'
    assert expected_file.exists()
    assert expected_file.is_file()


def test_translation_content(tmp_path):
    my_dir = tmp_path / 'my_dir'
    my_dir.mkdir()
    translation = {'x':1.1,'y':2.2,'z':3.3}
    con = parser_context(my_dir)
    parsers.trans_parser(con,translation)
    expected_file = my_dir / 'translation.json'
    j = json.load(open(expected_file))
    assert 'x' in j
    assert 'y' in j
    assert 'z' in j
    for k in j:
        assert math.isclose(j[k],translation[k])
