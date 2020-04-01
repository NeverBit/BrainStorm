import click
from .db_access import Reader
from .image import image
import importlib
import json
from . import mq
from . import parsers_store
from . import parsers
from pathlib import Path
import pika
from .proto import Snapshot, SnapshotSlim
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, BigInteger, String, ForeignKey, and_
import traceback


parsers_names = list(parsers.registered_parsers.keys())


class Saver(Reader):
    ''' Saves brainstorm specific data pieces to a database '''

    def __init__(self, database_url):
        Reader.__init__(self, database_url)

    def get_or_create_user_id(self, uid, name, bday, gender):
        '''
        Tries to get the user id for a given user from the db. if not found, creates
        a new entry in the db and return the new id
        '''
        query = self.users_table.select().where(and_(self.users_table.c.id == uid))
        connection = self.engine.connect()
        found = connection.execute(query).fetchone() is not None
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

    def update_or_create_snapshot(self, uid, datetime, new_available_result):
        '''
        Tries to update a snapshot db entry wiuth new 'avilable results'.
        if not found, creates a new entry in the db.
        Returns the id of the existing/new db entry
        '''
        match = self.get_snapshot_by_time(uid, datetime)
        connection = self.engine.connect()

        # Execute an UPDATE or INSERT based on whether we found an entry for
        # the snapshot
        if match:
            # Snapshot already in DB, need an UPDATE
            print('UPDATING existing snapshot')
            # Get previous results from match
            available_results = json.loads(match.available_results)
            # Add current new result if needed
            if new_available_result not in available_results:
                available_results.append(new_available_result)
            # Build new array of 'parsed results'
            avail_res_json = json.dumps(available_results)

            # Create and run db UPDATE command
            update = self.snapshots_table.update()
            update = update.values(available_results=avail_res_json)
            update = update.where(self.snapshots_table.c.id == match.id)
            res = connection.execute(update)
            res_id = match.id
        else:
            # Snapshot not in DB, need an INSERT
            avail_res_json = json.dumps([new_available_result])
            print('INSERTING new snapshot')
            insert = self.snapshots_table.insert().values(
                uid=uid, datetime=datetime, available_results=avail_res_json)
            res = connection.execute(insert)
            res_id = res.inserted_primary_key[0]
        connection.close()
        return res_id

    def save_parser_res(self, parser_name, snapshot_id, data):
        '''
        Saves results of a parser (extracted from a specific snapshot)
        to the database
        '''
        insert = self.parsers_tables[parser_name].insert().values(
            snapshotid=snapshot_id, encoded_results=data)
        connection = self.engine.connect()
        res = connection.execute(insert)
        print(
            f"Saving parser res. snap ID: {snapshot_id}, Result Type: {parser_name}")
        print(f"Updated Parser Res Snapshot ID : {res.inserted_primary_key}")
        connection.close()
        return res.inserted_primary_key[0]

    def save(self, content_name, saver_msg):
        '''
        Handle a complete message for the saver:
        Including a user id, snapshot id, and data from one of the parsers
        The Saver asserts user & snapshot metadata exists (or created) in
        the DB and than saves the parser's result
        '''
        user_info = saver_msg['user_info']
        uid = user_info['uid']
        self.get_or_create_user_id(uid,
                                   user_info['name'],
                                   user_info['bday'],
                                   user_info['gender'],)

        dt = saver_msg['datetime']
        parser_name = saver_msg['parser_name']
        snapid = self.update_or_create_snapshot(uid, dt, parser_name)
        if not snapid:
            # Snapshot already has this info
            print('Failure, content already added to snapshot')
            return

        parser_res = saver_msg['parser_res']
        self.save_parser_res(parser_name, snapid, parser_res)


@click.group()
def main():
    pass


@main.command(name='save')
@click.option(
    '-d',
    '--database',
    type=str,
    default='postgres://postgres:pass@127.0.0.1:5432/postgres',
    help='Connection string to db. Format: db_type://user:pass@host:port/database_name')
@click.argument('name', type=str)
@click.argument('input', type=click.File('rb'))
def run_saver_once(database, name, input):
    '''
    Runs the saver once for input (read from INPUT)
    from a given topic (given in NAME) and writing to a db
    '''
    saver_msg = json.loads(input.read())

    s = Saver(database)

    print(' @@@ Calling Saver.Save()')
    s.save(name, saver_msg)
    print(' @@@ Returned from Saver.Save()')


@main.command(name='run-saver')
@click.argument(
    'database_str',
    type=str,
    default='postgres://postgres:pass@127.0.0.1:5432/postgres')
@click.argument('mq_str', type=str, default='rabbitmq://127.0.0.1:5672/')
def run_saver_service(database_str, mq_str):
    '''
    Runs the saver as a service, reading from MQ_STR and writing to db at DATABASE_STR.
    MQ_STR format: mq_type://host:port/
    DATABASE_STR format: db_type://user:pass@host:port/database_name
    '''
    # Create DB connection towards saver
    s = Saver(database_str)

    # Define save callback
    def callback(channel, method, properties, body):
        print(f'SAVER got New MQ Message! Channel: {channel} Body: {body}')
        saver_msg = json.loads(body)
        s.save(channel, saver_msg)

    # Consume input mq
    print(f' @@@ Debug Creating MQ connection input')
    con_to_input = mq.create_mq_connection(mq_str, 'parsers')
    print(' @@@ Debug Opening MQ connection')
    con_to_input.open()
    print(' @@@ Debug Opened MQ connection')
    con_to_input.start_consume(callback)
    print(' @@@ Debug start_consume MQ connection')


if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm.saver', obj={})
    except Exception as error:
        print(error)
        print(f'ERROR: {error}')
        track = traceback.format_exc()
        print(track)
        sys.exit(1)
