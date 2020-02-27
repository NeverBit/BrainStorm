import datetime as dt
import multiprocessing
import pathlib
import subprocess
import os
import io
import socket
import struct
import time

import pytest

from BrainStorm.client import upload_sample
from BrainStorm import proto

_SERVER_ADDRESS = '127.0.0.1',5000
_SERVER_ADDRESS_FOR_UT = '127.0.0.1:5000'
_SERVER_BACKLOG = 1000
_CLIENT_PATH = pathlib.Path(__file__).absolute().parent.parent / 'client.py'

_HEADER_FORMAT = 'LLI'
_HEADER_SIZE = struct.calcsize(_HEADER_FORMAT)

_DISABLED_test_HEADER_1 = b'*\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00Dan Gittik`H\xb5)m'
_H1_NAME = 'Dan Gittik'


@pytest.fixture
def get_message():
    parent, child = multiprocessing.Pipe()
    process = multiprocessing.Process(target=_run_server, args=(child,))
    process.start()
    parent.recv()
    try:
        def get_message():
            if not parent.poll(1):
                raise TimeoutError()
            return parent.recv()
        yield get_message
    finally:
        process.terminate()
        process.join()

@pytest.fixture
def get_mind_sample():
    snapshot = b'\x00' * 64
    snapshot += struct.pack('II',1,1)
    snapshot += b'\xff\x00\x00'
    snapshot += struct.pack('II',1,1)
    snapshot += b'\xff\x00\x00\x00'
    snapshot += b'\x00' * 16
    return io.BytesIO(_DISABLED_test_HEADER_1 + snapshot)

def DISABLED_test_connection(get_message,get_mind_sample):
    upload_sample(*_SERVER_ADDRESS, get_mind_sample)
    message = get_message()
    assert message


def DISABLED_test_hello_msg_recvd(get_message,get_mind_sample):
    upload_sample(*_SERVER_ADDRESS, get_mind_sample)
    message = get_message()
    h = proto.Hello.deserialize(message)
    assert h

def DISABLED_test_name_recvd(get_message,get_mind_sample):
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
        print('a')
        header_data = _receive_all(connection, 4)
        print('b')
        leng, = struct.unpack('!I',header_data)
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
