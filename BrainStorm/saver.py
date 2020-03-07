import bson
import click
from .image import image
import importlib
import json
from . import mq
from . import parsers_store
from . import parsers
from pathlib import Path
import pika
from .proto import Snapshot
from .proto import SnapshotSlim
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, BigInteger, String, ForeignKey, and_

parsers_names = list(parsers.registered_parsers.keys())

class Saver:
    def __init__(self,database_url):
        print(f'Saver Connecting to: {database_url}')
        self.engine = create_engine(database_url)
        # Create tables in DB (if required)
        meta = MetaData()

        self.users_table = Table(
            'users', meta, 
            Column('id', Integer, primary_key = True), 
            Column('name', String, nullable=False), 
            Column('birthday', Integer, nullable=False),
            Column('gender', String, nullable=False), 
        )

        self.snapshots_table = Table(
            'snapshots', meta, 
            Column('id', Integer, primary_key = True), 
            Column('uid', Integer, ForeignKey('users.id')),
            Column('datetime', BigInteger, nullable=False), 
            Column('available_results', String, nullable=False)
        )

        self.patsers_tables = {}
        for parser in parsers_names:    
            self.patsers_tables[parser] = Table(
                parser, meta, 
                Column('id', Integer, primary_key = True), 
                Column('snapshotid', Integer, ForeignKey('snapshots.id')),
                Column('encoded_results', String, nullable=False), 
            )

        meta.create_all(self.engine)

    def save_or_get_user(self,uid,name,bday,gender):
        # TODO: Check if already exists?
        query = self.users_table.select().where(and_(self.users_table.c.id == uid))
        connection = self.engine.connect()
        found = connection.execute(query).fetchone() != None
        print(f"Finished getting user : {found}")
        connection.close()
        if found:
            return

        print(f"User not found, adding new user with id: {uid}")
        insert = self.users_table.insert().values(id=uid,
                                        name=name, 
                                        birthday=bday,
                                        gender=gender)
        connection = self.engine.connect()
        result = connection.execute(insert)
        print(f"Finished saving user : {result}")
        print(f"Finished saving user ID : {result.inserted_primary_key}")
        # TODO: Check results?
        connection.close()
        return result.inserted_primary_key[0]
    def save_or_get_snapshot(self,uid,datetime,new_available_result):
        # Get current available_results
        print(f" getting snapshot : {uid} - {datetime}")
        query = self.snapshots_table.select().where(
                        and_(self.snapshots_table.c.uid == uid,
                             self.snapshots_table.c.datetime == datetime))
        connection = self.engine.connect()
        match = connection.execute(query).fetchone()
        print(f"Finished getting snapshot : {match}")
        if match:
            # Snapshot already in DB, need an UPDATE
            print('UPDATING existing snapshot')
            print(f'Has commit? {type(match)}')
            entry = dict(match)
            available_results = match.available_results
            if new_available_result in available_results:
                # Already added
                print(f"Update SHORT")
                return None
            available_results.append(new_available_result)
            avail_res_json = json.dumps(available_results)
            update = self.snapshots_table.update(self.snapshots_table.c.id==match.id).execute(available_results=avail_res_json)
            print(update)
            res = connection.execute(update)
            print(f"Update snap Res : {res}")
            print(f"Update snap Res ID : {res.inserted_primary_key}")
            connection.close()
            pass
        else:
            # Snapshot not in DB, need an INSERT
            print('INSERTING new snapshot')
            available_results = []
            available_results.append(new_available_result)
            avail_res_json = json.dumps(available_results)
            insert = self.snapshots_table.insert().values(uid=uid,
                                            datetime=datetime,
                                            available_results=avail_res_json)
            print(f"Insert Snapshot : {insert} , Avail Results: {avail_res_json}")
            connection = self.engine.connect()
            res = connection.execute(insert)
            print(f"Insert snap Res : {res}")
            print(f"Insert snap Res ID : {res.inserted_primary_key}")
            connection.close()
            return res.inserted_primary_key[0]
    def save_parser_res(self,parser_name,snapshotid,data):
        insert = self.patsers_tables[parser_name].insert().values(
                            snapshotid=snapshotid,encoded_results=data)
        connection = self.engine.connect()
        res = connection.execute(insert)
        print(f"Update Parser Res Snapshot : {res}")
        print(f"Update Parser Res Snapshot ID : {res.inserted_primary_key}")
        connection.close()
    def save(self,content_name,saver_msg):
        # TODO
        uid = saver_msg['uid']
        self.save_or_get_user(uid,'woot',1337,'m')
        
        dt = saver_msg['datetime']
        parser_name = saver_msg['parser_name']
        snapid = self.save_or_get_snapshot(uid,dt,parser_name)
        if not snapid:
            # Snapshot already has this info
            print('Failure, content already added to snapshot')
            return

        parser_res = saver_msg['parser_res']
        self.save_parser_res(parser_name,snapid,parser_res)
        pass


@click.group()
def main():
    pass


@main.command(name='save')
@click.option('-d','--database', type=str, default='postgres://postgres:pass@127.0.0.1:5432/postgres',
                help='Connection string to db. Format: db_type://user:pass@host:port/database_name')
@click.argument('name', type=str)
@click.argument('input', type=click.File('rb'))
def run_saver_once(database,name,input):
    '''
    Runs the saver once for input (read from INPUT) 
    from a given topic (given in NAME) and writing to a db
    '''
    saver_msg = json.loads(input.read())

    s = Saver(database)

    print(' @@@ Calling Saver.Save()')
    s.save(name,saver_msg)
    print(' @@@ Returned from Saver.Save()')


@main.command(name='run-saver')
@click.argument('database_str', type=str, default='postgres://postgres:pass@127.0.0.1:5432/postgres')
@click.argument('mq_str', type=str, default='rabbitmq://127.0.0.1:5672/')
def run_saver_service(database_str,mq_str):
    '''
    Runs the saver as a service, reading from MQ_STR and writing to db at DATABASE_STR. 
    MQ_STR format: mq_type://host:port/
    DATABASE_STR format: db_type://user:pass@host:port/database_name
    '''
    pass


if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm.saver', obj={})
    except Exception as error:
        print(error)
        print(f'ERROR: {error}')
        sys.exit(1)
 