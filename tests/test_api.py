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