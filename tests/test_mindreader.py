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

_TEST_HEADER_1 = b'*\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00Dan Gittik`H\xb5)m'
_H1_NAME = 'Dan Gittik'

def test_header_parsing():
    r = mindreader.reader(io.BytesIO(_TEST_HEADER_1))
    assert r.uname == _H1_NAME
    assert r.uid == 42 
    assert r.gender == 'm'
