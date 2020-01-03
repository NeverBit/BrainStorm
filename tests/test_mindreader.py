import datetime as dt
import multiprocessing
import pathlib
import subprocess
import os
import socket
import struct
import time
import io

import pytest

from BrainStorm import mindreader

_TEST_HEADER_v1 = b'*\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00Dan Gittik`H\xb5)m'
_H1_NAME = 'Dan Gittik'

_TEST_HEADER_v2 = b'\x14\x00\x00\x00\x08\x2A\x12\x0A\x44\x61\x6E\x20\x47\x69\x74\x74\x69\x6B\x18\xE0\x90\xD5\xCD\x02\x6C\x46\x61\x00\x08\xAB\xF7\xCE\xFF\xEC\x2D\x12\x43\x0A\x1B\x09'


def test_get_reader_version_1():
    assert mindreader.get_reader(1) == mindreader.reader_v1


def test_get_reader_version_2():
    assert mindreader.get_reader(2) == mindreader.reader_v2



def test_v1_header_parsing():
    r = mindreader.reader_v1(io.BytesIO(_TEST_HEADER_v1))
    assert r.uname == _H1_NAME
    assert r.uid == 42 
    assert r.gender == 'm'



def test_v2_header_parsing():
    r = mindreader.reader_v2(io.BytesIO(_TEST_HEADER_v2))
    assert r.uname == _H1_NAME
    assert r.uid == 42 
    assert r.gender == 'm'
