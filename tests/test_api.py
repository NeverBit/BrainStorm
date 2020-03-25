import json
import pytest
import BrainStorm.api as api
from BrainStorm.db_access import Reader
from BrainStorm.saver import Saver

def test_override_reader__no_exceptions():
    # Arrange
    api.readerInst = Reader('sqlite://')
    
    # Act
    # Making sure the call below (which tries to use api.readerInst)
    # does not crash because it is None
    api.get_users_list()

def test_get_users_list__single_user__actual_list_returned():
    # Arrange
    saver =  Saver('sqlite://')
    api.readerInst = saver # hot-wiring the 'api' to our mock db
    user_id = 13
    uname = 'testy'
    bday = 10101
    gender = 'm'
    saver.get_or_create_user_id(user_id, uname, bday, gender)

    # Act
    res_list = api.get_users_list()

    # Assert
    assert user_id in res_list
    assert res_list[user_id] == uname


def test_get_users_list__multi_users__actual_list_returned():
    # Arrange
    saver =  Saver('sqlite://')
    api.readerInst = saver # hot-wiring the 'api' to our mock db
    user_id = 13
    uname = 'testy'
    bday = 10101
    gender = 'm'
    saver.get_or_create_user_id(user_id, uname, bday, gender)
    saver.get_or_create_user_id(user_id + 1, uname + '1', bday + 1, gender)

    # Act
    res_list = api.get_users_list()

    # Assert
    assert user_id in res_list
    assert res_list[user_id] == uname
    assert user_id+1 in res_list
    assert res_list[user_id+1] == uname+'1'


def test_get_user__single_user__actual_user_returned():
    # Arrange
    saver =  Saver('sqlite://')
    api.readerInst = saver # hot-wiring the 'api' to our mock db
    user_id = 13
    uname = 'testy'
    bday = 10101
    gender = 'm'
    saver.get_or_create_user_id(user_id, uname, bday, gender)

    # Act
    res = api.get_user(user_id)

    # Assert
    assert res != None
    assert res['id'] == user_id


def test_get_non_existent_user__single_user_inserted__raise_ex():
    # Arrange
    saver =  Saver('sqlite://')
    api.readerInst = saver # hot-wiring the 'api' to our mock db
    user_id = 13
    uname = 'testy'
    bday = 10101
    gender = 'm'
    saver.get_or_create_user_id(user_id, uname, bday, gender)

    # Act
    with pytest.raises(Exception):
        res = api.get_user(22)


def test_get_user__two_users__actual_uesrs_returned():
    # Arrange
    saver =  Saver('sqlite://')
    api.readerInst = saver # hot-wiring the 'api' to our mock db
    user_id = 13
    uname = 'testy'
    bday = 10101
    gender = 'm'
    saver.get_or_create_user_id(user_id, uname, bday, gender)
    saver.get_or_create_user_id(user_id + 1, uname + '1', bday, gender)

    # Act
    res = api.get_user(user_id)
    res2 = api.get_user(user_id + 1)

    # Assert
    assert res != None
    assert res['id'] == user_id
    assert res2 != None
    assert res2['id'] == user_id +1


def test_get_snaps_list__single_user_single_snap__actual_list_returned():
    # Arrange
    saver =  Saver('sqlite://')
    api.readerInst = saver # hot-wiring the 'api' to our mock db
    user_id = 13
    uname = 'testy'
    bday = 10101
    gender = 'm'
    saver.get_or_create_user_id(user_id, uname, bday, gender)
    dtime = 1122
    parser_name = 'pose'
    snap_id = saver.update_or_create_snapshot(user_id,dtime,parser_name)

    # Act
    res = api.get_user_snapshots_list(user_id)

    # Assert
    assert res != None
    assert snap_id in res
    assert res[snap_id]['uid'] == user_id
    assert res[snap_id]['id'] == snap_id
    assert res[snap_id]['datetime'] == dtime
    assert parser_name in res[snap_id]['available_results']


def test_get_snaps_list__single_user_multi_snaps__actual_list_returned():
    # Arrange
    saver =  Saver('sqlite://')
    api.readerInst = saver # hot-wiring the 'api' to our mock db
    user_id = 13
    uname = 'testy'
    bday = 10101
    gender = 'm'
    saver.get_or_create_user_id(user_id, uname, bday, gender)
    snap_id1 = saver.update_or_create_snapshot(user_id,1122,'pose')
    snap_id2 = saver.update_or_create_snapshot(user_id,3344,'pose')

    # Act
    res = api.get_user_snapshots_list(user_id)

    # Assert
    assert res != None
    assert snap_id1 in res
    assert snap_id2 in res
    assert res[snap_id2] != res[snap_id1]


def test_get_snaps_list__no_such_user__raise_exception():
    # Arrange
    saver =  Saver('sqlite://')
    api.readerInst = saver # hot-wiring the 'api' to our mock db
    user_id = 13
    uname = 'testy'
    bday = 10101
    gender = 'm'
    saver.get_or_create_user_id(user_id, uname, bday, gender)
    snap_id1 = saver.update_or_create_snapshot(user_id,1122,'pose')
    snap_id2 = saver.update_or_create_snapshot(user_id,3344,'pose')

    # Act
    with pytest.raises(Exception):
        api.get_user_snapshots_list(999)



def test_get_snap__no_such_user__raise_exception():
    # Arrange
    saver =  Saver('sqlite://')
    api.readerInst = saver # hot-wiring the 'api' to our mock db
    user_id = 13
    uname = 'testy'
    bday = 10101
    gender = 'm'
    saver.get_or_create_user_id(user_id, uname, bday, gender)
    snap_id1 = saver.update_or_create_snapshot(user_id,1122,'pose')
    snap_id2 = saver.update_or_create_snapshot(user_id,3344,'pose')

    # Act
    with pytest.raises(Exception):
        api.get_snapshot(999,snap_id1)



def test_get_snap__no_such_snap__raise_exception():
    # Arrange
    saver =  Saver('sqlite://')
    api.readerInst = saver # hot-wiring the 'api' to our mock db
    user_id = 13
    uname = 'testy'
    bday = 10101
    gender = 'm'
    saver.get_or_create_user_id(user_id, uname, bday, gender)
    snap_id1 = saver.update_or_create_snapshot(user_id,1122,'pose')
    snap_id2 = saver.update_or_create_snapshot(user_id,3344,'pose')

    # Act
    with pytest.raises(Exception):
        api.get_snapshot(user_id, 9900)


def test_get_snap__valid_ids__snapshot_returned():
    # Arrange
    saver =  Saver('sqlite://')
    api.readerInst = saver # hot-wiring the 'api' to our mock db
    user_id = 13
    uname = 'testy'
    bday = 10101
    gender = 'm'
    saver.get_or_create_user_id(user_id, uname, bday, gender)
    snap_id1 = saver.update_or_create_snapshot(user_id,1122,'pose')
    snap_id2 = saver.update_or_create_snapshot(user_id,3344,'pose')

    # Act
    snap = api.get_snapshot(user_id, snap_id1)

    # Assert
    assert snap != None
    assert snap['id'] == snap_id1


def test_get_parser_res__valid_ids__res_returned():
    # Arrange
    saver =  Saver('sqlite://')
    api.readerInst = saver # hot-wiring the 'api' to our mock db
    user_id = 13
    uname = 'testy'
    bday = 10101
    gender = 'm'
    saver.get_or_create_user_id(user_id, uname, bday, gender)
    parser_name = 'pose'
    snap_id = saver.update_or_create_snapshot(user_id, 1122, parser_name)
    content = "{'test':'tset'}"
    saver.save_parser_res(parser_name, snap_id, content)

    # Act
    res = api.get_result(user_id, snap_id, parser_name)

    # Assert
    assert res != None
    assert res == content


def test_get_parser_res__invalid_snapshot_id__raise_exception():
    # Arrange
    saver =  Saver('sqlite://')
    api.readerInst = saver # hot-wiring the 'api' to our mock db
    user_id = 13
    uname = 'testy'
    bday = 10101
    gender = 'm'
    saver.get_or_create_user_id(user_id, uname, bday, gender)
    parser_name = 'pose'
    snap_id = saver.update_or_create_snapshot(user_id, 1122, parser_name)
    content = "{'test':'tset'}"
    saver.save_parser_res(parser_name, snap_id, content)

    # Act
    with pytest.raises(Exception):
        res = api.get_result(user_id, 9988, parser_name)



def test_get_result_data__invalid_snapshot_id__raise_exception():
    # Arrange
    saver =  Saver('sqlite://')
    api.readerInst = saver # hot-wiring the 'api' to our mock db
    user_id = 13
    uname = 'testy'
    bday = 10101
    gender = 'm'
    saver.get_or_create_user_id(user_id, uname, bday, gender)
    parser_name = 'pose'
    snap_id = saver.update_or_create_snapshot(user_id, 1122, parser_name)
    content = "{'test':'tset'}"
    saver.save_parser_res(parser_name, snap_id, content)

    # Act
    with pytest.raises(Exception):
        res = api.get_result_data(user_id, 9988, parser_name)


def test_get_content_type_by_ext__unexpected_ext__return_octet_str():
    # Arrange
    path = '/a/b/c/d.exe'

    # Act
    resolved_type = api.get_content_type_by_ext(path)

    # Assert
    assert resolved_type == 'application/octet-stream'


def test_get_content_type_by_ext__jpg__return_img_jpeg():
    # Arrange
    path = '/a/b/c/d.jpg'

    # Act
    resolved_type = api.get_content_type_by_ext(path)

    # Assert
    assert resolved_type == 'image/jpeg'


def test_get_content_type_by_ext__jpeg__return_img_jpeg():
    # Arrange
    path = '/a/b/c/d.jpeg'

    # Act
    resolved_type = api.get_content_type_by_ext(path)

    # Assert
    assert resolved_type == 'image/jpeg'
