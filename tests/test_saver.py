import pytest
from BrainStorm.saver import Saver
from BrainStorm.db_access import Reader


def test_mem_db():
    in_mem_db_url = 'sqlite://'
    # Just making sure the line below doesn't throw
    s = Saver(in_mem_db_url)


def test_save_new_user():
    in_mem_db_url = 'sqlite://'
    # Just making sure the line below doesn't throw
    s = Saver(in_mem_db_url)
    param_id = 1
    res_id = s.get_or_create_user_id(uid=param_id, name='Testy', bday=101010, gender='m')
    assert res_id == param_id
    

def test_save_new_user_assert_id_written_to_db():
    in_mem_db_url = 'sqlite://'
    # Just making sure the line below doesn't throw
    s = Saver(in_mem_db_url)
    r = Reader(in_mem_db_url)
    r.engine = s.engine
    param_id = 1
    res_id = s.get_or_create_user_id(uid=param_id, name='Testy', bday=101010, gender='m')
    
    found_users = r.get_users()
    assert found_users != None
    assert param_id in found_users 


def test_save_new_user_assert_name_written_to_db():
    in_mem_db_url = 'sqlite://'
    # Just making sure the line below doesn't throw
    s = Saver(in_mem_db_url)
    r = Reader(in_mem_db_url)
    r.engine = s.engine
    param_id = 1
    res_id = s.get_or_create_user_id(uid=param_id, name='Testy', bday=101010, gender='m')
    
    found_users = r.get_users()
    assert found_users != None
    assert found_users[param_id] == 'Testy'


def test_save_2_new_users_diff_ids():
    in_mem_db_url = 'sqlite://'
    # Just making sure the line below doesn't throw
    s = Saver(in_mem_db_url)
    param_id = 1
    res_id = s.get_or_create_user_id(uid=param_id, name='Testy', bday=101010, gender='m')
    assert res_id == param_id
    param_id = 2
    # Line below should not throw, just return None 
    res_id = s.get_or_create_user_id(uid=param_id, name='Pesty', bday=201010, gender='f')
    assert res_id == param_id


def test_save_2_new_users_same_ids():
    in_mem_db_url = 'sqlite://'
    # Just making sure the line below doesn't throw
    s = Saver(in_mem_db_url)
    param_id = 1
    res_id = s.get_or_create_user_id(uid=param_id, name='Testy', bday=101010, gender='m')
    assert res_id == param_id
    # Line below should not throw, just return None 
    res_id = s.get_or_create_user_id(uid=param_id, name='Pesty', bday=201010, gender='f')
    assert res_id == None


def test_save_2_new_users_same_ids():
    in_mem_db_url = 'sqlite://'
    # Just making sure the line below doesn't throw
    s = Saver(in_mem_db_url)
    param_id = 1
    res_id = s.get_or_create_user_id(uid=param_id, name='Testy', bday=101010, gender='m')
    assert res_id == param_id
    # Line below should not throw, just return None 
    res_id = s.get_or_create_user_id(uid=param_id, name='Pesty', bday=201010, gender='f')
    assert res_id == None


def test_save_snapshot():
    in_mem_db_url = 'sqlite://'
    # Just making sure the line below doesn't throw
    s = Saver(in_mem_db_url)
    param_id = 1
    res_id = s.get_or_create_user_id(uid=param_id, name='Testy', bday=101010, gender='m')
    assert res_id == param_id
    # Line below should not throw, just return None 
    snap_id = s.update_or_create_snapshot(uid=param_id, datetime=1122, new_available_result='parser1')
    assert snap_id != None
    assert type(snap_id) == int


def test_save_2_snapshots_both_return_ids():
    in_mem_db_url = 'sqlite://'
    # Just making sure the line below doesn't throw
    s = Saver(in_mem_db_url)
    param_id = 1
    res_id = s.get_or_create_user_id(uid=param_id, name='Testy', bday=101010, gender='m')
    assert res_id == param_id
    # Line below should not throw, just return None 
    snap_id1 = s.update_or_create_snapshot(uid=param_id, datetime=1122, new_available_result='parser1')
    snap_id2 = s.update_or_create_snapshot(uid=param_id, datetime=1133, new_available_result='parser1')
    assert snap_id1 != None
    assert snap_id2 != None
    assert type(snap_id2) == int
    assert type(snap_id2) == int


def test_save_multi_snapshots_get_different_ids():
    in_mem_db_url = 'sqlite://'
    # Just making sure the line below doesn't throw
    s = Saver(in_mem_db_url)
    param_id = 1
    res_id = s.get_or_create_user_id(uid=param_id, name='Testy', bday=101010, gender='m')
    assert res_id == param_id
    # Line below should not throw, just return None 
    snap_id1 = s.update_or_create_snapshot(uid=param_id, datetime=1122, new_available_result='parser1')
    snap_id2 = s.update_or_create_snapshot(uid=param_id, datetime=1133, new_available_result='parser1')
    assert snap_id1 != snap_id2


def test_save_snapshot__written_to_db():
    in_mem_db_url = 'sqlite://'
    # Just making sure the line below doesn't throw
    s = Saver(in_mem_db_url)
    r = Reader(in_mem_db_url)
    r.engine = s.engine
    
    param_id = 1
    res_id = s.get_or_create_user_id(uid=param_id, name='Testy', bday=101010, gender='m')
    assert res_id == param_id
    # Line below should not throw, just return None 
    parser = 'parser1'
    dtime = 1122
    snap_id = s.update_or_create_snapshot(uid=param_id, datetime=dtime, new_available_result=parser)
    
    res_snap = r.get_snapshot(param_id,snap_id)
    assert res_snap != None
    assert res_snap['uid'] == param_id
    assert res_snap['id'] == snap_id
    assert res_snap['datetime'] == dtime
    assert parser in res_snap['available_results']


def test_append_result_to_snapshot__new_result_written_to_db():
    in_mem_db_url = 'sqlite://'
    # Just making sure the line below doesn't throw
    s = Saver(in_mem_db_url)
    r = Reader(in_mem_db_url)
    r.engine = s.engine
    
    param_id = 1
    res_id = s.get_or_create_user_id(uid=param_id, name='Testy', bday=101010, gender='m')
    assert res_id == param_id
    # Line below should not throw, just return None 
    parser1 = 'parser1'
    dtime = 1122
    snap_id = s.update_or_create_snapshot(uid=param_id, datetime=dtime, new_available_result=parser1)
    parser2 = 'parser2'
    dtime = 1122
    snap_id = s.update_or_create_snapshot(uid=param_id, datetime=dtime, new_available_result=parser2)
    
    res_snap = r.get_snapshot(param_id,snap_id)
    assert parser2 in res_snap['available_results']


def test_append_result_to_snapshot__same_snap_id_returned():
    in_mem_db_url = 'sqlite://'
    # Just making sure the line below doesn't throw
    s = Saver(in_mem_db_url)
    
    param_id = 1
    res_id = s.get_or_create_user_id(uid=param_id, name='Testy', bday=101010, gender='m')
    assert res_id == param_id
    # Line below should not throw, just return None 
    parser1 = 'parser1'
    dtime = 1122
    snap_id1 = s.update_or_create_snapshot(uid=param_id, datetime=dtime, new_available_result=parser1)
    parser2 = 'parser2'
    snap_id2 = s.update_or_create_snapshot(uid=param_id, datetime=dtime, new_available_result=parser2)
    
    assert snap_id1 == snap_id2

def test_append_result_to_snapshot__old_result_still_found_in_db():
    in_mem_db_url = 'sqlite://'
    # Just making sure the line below doesn't throw
    s = Saver(in_mem_db_url)
    r = Reader(in_mem_db_url)
    r.engine = s.engine
    
    param_id = 1
    res_id = s.get_or_create_user_id(uid=param_id, name='Testy', bday=101010, gender='m')
    assert res_id == param_id
    # Line below should not throw, just return None 
    parser1 = 'parser1'
    dtime = 1122
    snap_id = s.update_or_create_snapshot(uid=param_id, datetime=dtime, new_available_result=parser1)
    parser2 = 'parser2'
    dtime = 1122
    snap_id = s.update_or_create_snapshot(uid=param_id, datetime=dtime, new_available_result=parser2)
    
    res_snap = r.get_snapshot(param_id,snap_id)
    assert parser1 in res_snap['available_results']