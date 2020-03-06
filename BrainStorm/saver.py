import bson
import click
from . import db
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
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey

parsers_names = list(parsers.registered_parsers.keys())

class Saver:
    def __init__(self,database_url):
        self.engine = create_engine('postgresql://postgres@localhost/test')
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
            Column('datetime', Integer, nullable=False), 
            Column('available_results', String, nullable=False)
        )

        self.patsers_tables = {}
        for parser in parsers_names:    
            self.patsers_tables[new_parser] = Table(
                parser, meta, 
                Column('id', Integer, primary_key = True), 
                Column('snapshotid', Integer, ForeignKey('snapshots.id')),
                Column('encoded_results', String, nullable=False), 
            )

        meta.create_all(engine)

    def save_user(self,user):
        # TODO: Check if already exists?
        insert = self.users_table.insert().values(id=user.id,
                                        name=user.name, 
                                        birthday=user.bday,
                                        gender=user.gender)
        connection = engine.connect()
        result = connection.execute(insert)
        print(f"Finished saving user : {result}")
        # TODO: Check results?
    def create_or_update_snapshot(self,uid,datetime,new_available_result):
        # Get current available_results
        available_results = []
        available_results.append(new_available_result)
        avail_res_json = json.dumps(available_results)
        insert = Snapshot.insert().values(uid=uid,
                                        name=user.name, 
                                        birthday=user.bday,
                                        gender=user.gender)
        print(f"Update Snapshot : {insert} , Avail Results: {avail_res_json}")
    def get_snapshot(self,uid,datetime):
        # TODO
        pass
    def save_parser_res(self,parser_name,snapshotid,data):
        insert = self.patsers_tables[parser_name].insert().values(
                            snapshotid=snapshotid,encoded_results=data)
        print(f"Update Parser Res Snapshot : {insert} , Avail Results: {avail_res_json}")


@click.group()
def main():
    pass


@main.command(name='saver')
@click.argument('name', type=str)
@click.argument('input', type=click.File('r'))
def run_saver_once(name,input):

    saver_msg = {
        'uid':snapshot.uid,
        'datetime':snapshot.datetime,
        'parser_name':name,
        'parser_res':parser_results
    }
    saver_msg = json.loads(input)
    uid = saver_msg['uid']
    dt = saver_msg['datetime']
    parser_name = saver_msg['parser_name']
    parser_res = saver_msg['parser_res']


    saver_msg_json = json.dumps(saver_msg)
    print(' @@@ Debug in done parsing')
    json_snap = json.dumps(res)
    print(json_snap)


@main.command(name='run-parser')
@click.argument('name', type=str)
@click.argument('connection_string', type=str)
def run_parser_service(name,connection_string):
    # Resolve parser name to function
    parse_func = registered_parsers[name]

    # Create MQ connection towards saver
    con_to_saver = mq.create_mq_connection(connection_string, 'save')
    con_to_saver.open()

    # Define parse & publish callback
    def callback(channel, method, properties, body):
        snapshot = SnapshotSlim.fromDict(json.loads(body))
        context = parser_context(Path('resources'))
        parser_results = parse_func(context,snapshot)
        # Wrap the parer results in a unified format for the server
        saver_msg = {
            'uid':snapshot.uid,
            'datetime':snapshot.datetime,
            'parser_name':name,
            'parser_res':parser_results
        }
        saver_msg_json = json.dumps(saver_msg)
        con_to_saver.publish(saver_msg_json)

    # Consume input mq
    con_to_input = mq.create_mq_connection(connection_string, 'input')
    con_to_input.open()
    con_to_input.start_consume(callback)


if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm.parsers', obj={})
    except Exception as error:
        print(error)
        print(f'ERROR: {error}')
        sys.exit(1)
 