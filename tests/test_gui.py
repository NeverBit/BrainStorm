import flask
import json
import pytest
from BrainStorm.gui import WebServer
import BrainStorm.gui as gui
import BrainStorm.api as api
from BrainStorm.db_access import Reader
from BrainStorm.saver import Saver
import tempfile
import os


@pytest.fixture
def client():
    db_fd, gui.app.config['DATABASE'] = tempfile.mkstemp()
    gui.app.config['TESTING'] = True

    with gui.app.test_client() as client:
        with gui.app.app_context():
            #gui.init_db()
            x = 1
        yield client

    os.close(db_fd)
    os.unlink(gui.app.config['DATABASE'])


def fill_db(saver):
    saver_msg = {
        'user_info': {
                        'uid':123,
                        'name':'testy',
                        'bday':10101,
                        'gender':'m'
                        },
        'datetime': 1234,
        'parser_name': 'pose',
        'parser_res': json.dumps({'hunger': 1.1, 'thirst': 2.2, 'exhaustion': 3.3, 'happiness': 4.4 })
    }
    saver.save('pose',saver_msg)
    return saver_msg


def test_get_home__page_returned(client):
    # Arrange
    wserver = WebServer('sqlite://')
    gui.serverInst = wserver 
    # saver =  Saver('sqlite://')
    # saver.engine = wserver.reader.engine
    # fill_db(saver)

    # Act
    res = client.get('/')

    # Assert
    assert res != None
    assert res._status_code == 200
    assert res.data != None


def test_get_users__page_returned(client):
    # Arrange
    wserver = WebServer('sqlite://')
    gui.serverInst = wserver

    # Act
    res = client.get('/users')

    # Assert
    assert res != None
    assert res._status_code == 200
    assert res.data != None


def test_get_users__page_returned(client):
    # Arrange
    wserver = WebServer('sqlite://')
    gui.serverInst = wserver 
    saver =  Saver('sqlite://')
    saver.engine = wserver.reader.engine
    saved_msg = fill_db(saver)

    # Act
    res = client.get('/users')

    # Assert
    assert res != None
    assert res._status_code == 200
    assert res.data != None
    assert str(saved_msg['user_info']['uid']) in str(res.data)
    assert str(saved_msg['user_info']['name']) in str(res.data)


def test_get_user__user_exists__page_returned(client):
    # Arrange
    wserver = WebServer('sqlite://')
    gui.serverInst = wserver 
    saver =  Saver('sqlite://')
    saver.engine = wserver.reader.engine
    saved_msg = fill_db(saver)
    uid = str(saved_msg['user_info']['uid'])

    # Act
    res = client.get(f'/users/{uid}')

    # Assert
    assert res != None
    assert res._status_code == 200
    assert res.data != None
    assert uid in str(res.data)
    assert str(saved_msg['user_info']['name']) in str(res.data)


def test_get_user__user_doesnt_exist__404_returned(client):
    # Arrange
    wserver = WebServer('sqlite://')
    gui.serverInst = wserver 
    saver =  Saver('sqlite://')
    saver.engine = wserver.reader.engine
    saved_msg = fill_db(saver)

    # Act
    res = client.get(f'/users/9988')

    # Assert
    assert res != None
    assert res._status_code == 404


def test_get_snapshot__user_doesnt_exist__404_returned(client):
    # Arrange
    wserver = WebServer('sqlite://')
    gui.serverInst = wserver 
    saver =  Saver('sqlite://')
    saver.engine = wserver.reader.engine
    saved_msg = fill_db(saver)
    snap_id = 1 

    # Act
    res = client.get(f'/users/9988/snapshots/{snap_id}')

    # Assert
    assert res != None
    assert res._status_code == 404


def test_get_snapshot__user_doesnt_exist__404_returned(client):
    # Arrange
    wserver = WebServer('sqlite://')
    gui.serverInst = wserver 
    saver =  Saver('sqlite://')
    saver.engine = wserver.reader.engine
    saved_msg = fill_db(saver)
    uid = str(saved_msg['user_info']['uid'])
    snap_id = 99

    # Act
    res = client.get(f'/users/{uid}/snapshots/{snap_id}')

    # Assert
    assert res != None
    assert res._status_code == 404


def test_get_snapshot__snapshot_exist__page_returned(client):
    # Arrange
    wserver = WebServer('sqlite://')
    gui.serverInst = wserver 
    saver =  Saver('sqlite://')
    saver.engine = wserver.reader.engine
    saved_msg = fill_db(saver)
    uid = str(saved_msg['user_info']['uid'])
    snap_id = 1 

    # Act
    res = client.get(f'/users/{uid}/snapshots/{snap_id}')

    # Assert
    assert res != None
    assert res._status_code == 200


def test_get_snapshot_raw__snapshot_exist__page_returned(client):
    # Arrange
    wserver = WebServer('sqlite://')
    gui.serverInst = wserver 
    saver =  Saver('sqlite://')
    saver.engine = wserver.reader.engine
    saved_msg = fill_db(saver)
    uid = str(saved_msg['user_info']['uid'])
    snap_id = 1 

    # Act
    res = client.get(f'/users/{uid}/snapshots/{snap_id}/raw')

    # Assert
    assert res != None
    assert res._status_code == 200


def test_get_timeline_data__user_exist__page_returned(client):
    # Arrange
    wserver = WebServer('sqlite://')
    gui.serverInst = wserver 
    saver =  Saver('sqlite://')
    saver.engine = wserver.reader.engine
    saved_msg = fill_db(saver)
    uid = str(saved_msg['user_info']['uid'])
    snap_id = 1 

    # Act
    res = client.get(f'/users/{uid}/timeline_data.html')

    # Assert
    assert res != None
    assert res._status_code == 200


def test_get_timeline_data__user_doesnt_exist__404_returned(client):
    # Arrange
    wserver = WebServer('sqlite://')
    gui.serverInst = wserver 
    saver =  Saver('sqlite://')
    saver.engine = wserver.reader.engine
    saved_msg = fill_db(saver)
    uid = str(saved_msg['user_info']['uid'])
    snap_id = 1 

    # Act
    res = client.get(f'/users/9999/timeline_data.html')

    # Assert
    assert res != None
    assert res._status_code == 404


def test_get_result_data__user_doesnt_exist__404_returned(client):
    # Arrange
    wserver = WebServer('sqlite://')
    gui.serverInst = wserver 
    saver =  Saver('sqlite://')
    saver.engine = wserver.reader.engine
    saved_msg = fill_db(saver)
    uid = str(saved_msg['user_info']['uid'])
    snap_id = 1 

    # Act
    res = client.get(f'/users/9999/snapshots/{snap_id}/pose/data')

    # Assert
    assert res != None
    assert res._status_code == 404


def test_get_result_data__result_doesnt_exist__404_returned(client):
    # Arrange
    wserver = WebServer('sqlite://')
    gui.serverInst = wserver 
    saver =  Saver('sqlite://')
    saver.engine = wserver.reader.engine
    saved_msg = fill_db(saver)
    uid = str(saved_msg['user_info']['uid'])
    snap_id = 1 

    # Act
    res = client.get(f'/users/{uid}/snapshots/{snap_id}/pose/data')

    # Assert
    assert res != None
    assert res._status_code == 404