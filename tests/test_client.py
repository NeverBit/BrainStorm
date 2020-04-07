from contextlib import contextmanager
import datetime as dt
import multiprocessing
import pathlib
import subprocess
import os
import io
import struct
import time
import traceback

import pytest

from BrainStorm.client import upload_sample
from BrainStorm import client
from BrainStorm import proto

_SERVER_ADDRESS = '127.0.0.1', 5000
_SERVER_ADDRESS_FOR_UT = '127.0.0.1:5000'
_SERVER_BACKLOG = 1000
_CLIENT_PATH = pathlib.Path(__file__).absolute().parent.parent / 'client.py'

_HEADER_FORMAT = 'LLI'
_HEADER_SIZE = struct.calcsize(_HEADER_FORMAT)

_DISABLED_test_HEADER_1 = b'*\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00Dan Gittik`H\xb5)m'
_H1_NAME = 'Dan Gittik'


_TEST_HEADER_v2 = b'\x14\x00\x00\x00\x08\x2A\x12\x0A\x44\x61\x6E\x20\x47\x69\x74\x74\x69\x6B\x18\xE0\x90\xD5\xCD\x02\x6C\x46\x61\x00\x08\xAB\xF7\xCE\xFF\xEC\x2D\x12\x43\x0A\x1B\x09'


@pytest.fixture
def get_mind_sample():
    # snapshot=b'\x00' * 64
    # snapshot += struct.pack('II',1,1)
    # snapshot += b'\xff\x00\x00'
    # snapshot += struct.pack('II',1,1)
    # snapshot += b'\xff\x00\x00\x00'
    # snapshot += b'\x00' * 16

    snapshot = b''
    return _TEST_HEADER_v2 + snapshot


def DISABLED_test_connection(get_message, get_mind_sample):
    upload_sample(*_SERVER_ADDRESS, get_mind_sample)
    message = get_message()
    assert message


def DISABLED_test_hello_msg_recvd(get_message, get_mind_sample):
    upload_sample(*_SERVER_ADDRESS, get_mind_sample)
    message = get_message()
    h = proto.Hello.deserialize(message)
    assert h


def DISABLED_test_name_recvd(get_message, get_mind_sample):
    upload_sample(*_SERVER_ADDRESS, get_mind_sample)
    message = get_message()
    h = proto.Hello.deserialize(message)
    assert h.uname == _H1_NAME


def _run_server(pipe):
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(_SERVER_ADDRESS)
    server.listen(_SERVER_BACKLOG)
    pipe.send('ready')
    with server:
        while True:
            connection, address = server.accept()
            _handle_connection(connection, pipe)


def _handle_connection(connection, pipe):
    with connection:
        header_data = _receive_all(connection, 4)
        leng, = struct.unpack('!I', header_data)
        data = _receive_all(connection, leng)
        pipe.send(data)


def _receive_all(connection, size):
    chunks = []
    while size > 0:
        chunk = connection.recv(size)
        if not chunk:
            raise RuntimeError('incomplete data')
        chunks.append(chunk)
        size -= len(chunk)
    return b''.join(chunks)


def _assert_now(timestamp):
    now = int(time.time())
    assert abs(now - timestamp) < 5


class dummy_cookies:
    def get_dict(self):
        return {}

    def __iter__(self):
        return {}.__iter__()


class dummy_response:
    pass


class dummy_session:
    def __init__(self):
        self.get_count = 0
        self.get_uris = []
        self.post_count = 0
        self.post_uris = []
        self.cookies = dummy_cookies()
        pass

    def get(self, uri, *args, **kwargs):
        self.get_uris.append(uri)
        self.get_count += 1
        res = dummy_response()
        res.content = '{"a":1}'
        return res

    def post(self, uri, *args, **kwargs):
        print(f'Post Called for uri: {uri}. Log: {self.post_uris}')
        self.post_uris.append(uri)
        print(f'Post Called for uri: {uri}. Log: {self.post_uris} AFTER')
        self.post_count += 1
        res = dummy_response()
        res.content = '{"a":1}'
        return res


dummy_inst = None
@contextmanager
def get_fake_sess():
    yield dummy_inst


def test_hello_sent(get_mind_sample, tmp_path):
    global dummy_inst
    org_getter = client.get_http_session
    dummy_inst = dummy_session()
    client.get_http_session = get_fake_sess
    # Making file with the sample in it
    sam_path = tmp_path / 'sample.bin'
    with open(sam_path, 'bw+') as f:
        f.write(get_mind_sample)
    try:
        upload_sample(*_SERVER_ADDRESS, str(sam_path))
    except Exception as e:
        traceback.print_exc()
        print(e)
        pass
    finally:
        client.get_http_session = org_getter

    print(f' Test Assert time. sess.post_uris : {dummy_inst.post_uris}')
    assert len(dummy_inst.post_uris) > 0
    hello_in_any = False
    for uri in dummy_inst.post_uris:
        hello_in_any |= 'hello' in uri
    assert hello_in_any


def test_config_requested(get_mind_sample, tmp_path):
    global dummy_inst
    org_getter = client.get_http_session
    dummy_inst = dummy_session()
    client.get_http_session = get_fake_sess
    # Making file with the sample in it
    sam_path = tmp_path / 'sample.bin'
    with open(sam_path, 'bw+') as f:
        f.write(get_mind_sample)
    try:
        upload_sample(*_SERVER_ADDRESS, str(sam_path))
    except Exception as e:
        print('here:')
        traceback.print_exc()
        print(e)
        pass
    finally:
        client.get_http_session = org_getter

    print(f' Test Assert time. sess.get_uris : {dummy_inst.get_uris}')
    assert len(dummy_inst.get_uris) > 0
    config_in_any = False
    for uri in dummy_inst.post_uris:
        config_in_any |= 'hello' in uri
    assert config_in_any
