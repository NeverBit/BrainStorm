from collections import OrderedDict
from .parsers import registered_parsers
from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey, and_
import sqlalchemy

parsers_names = list(registered_parsers.keys())


class DbBase:
    def __init__(self, database_url):
        print(f'Saver Connecting to: {database_url}')
        self.engine = create_engine(database_url)
        # Create tables in DB (if required)
        meta = MetaData()

        self.users_table = Table(
            'users', meta,
            Column('id', sqlalchemy.Integer, primary_key=True),
            Column('name', sqlalchemy.String, nullable=False),
            Column('birthday', sqlalchemy.Integer, nullable=False),
            Column('gender', sqlalchemy.String, nullable=False),
        )

        self.snapshots_table = Table(
            'snapshots', meta,
            Column('id', sqlalchemy.Integer, primary_key=True),
            Column('uid', sqlalchemy.Integer, ForeignKey('users.id')),
            Column('datetime', sqlalchemy.BigInteger, nullable=False),
            Column('available_results', sqlalchemy.String, nullable=False)
        )

        self.parsers_tables = {}
        for parser in parsers_names:
            self.parsers_tables[parser] = Table(
                parser, meta,
                Column('id', sqlalchemy.Integer, primary_key=True),
                Column('snapshotid', sqlalchemy.Integer,
                       ForeignKey('snapshots.id')),
                Column('encoded_results', sqlalchemy.String, nullable=False),
            )

        meta.create_all(self.engine)


class Reader(DbBase):
    def __init__(self, database_url):
        DbBase.__init__(self, database_url)

    def get_users(self):
        ''' Get all users from the DB '''
        query = self.users_table.select()
        connection = self.engine.connect()
        users = {}
        for entry in connection.execute(query):
            print(f'Iterating user {entry} DICT: {dict(entry)}')
            entryDict = dict(entry)
            users[entryDict['id']] = entryDict['name']
        connection.close()
        return users

    def get_user(self, uid):
        '''  Get a single user from the DB'''
        query = self.users_table.select().where(
            and_(self.users_table.c.id == uid))
        connection = self.engine.connect()
        found = connection.execute(query).fetchone()
        print(f"Finished getting user : {found}")
        connection.close()
        if not found:
            return None
        return dict(found)

    def get_snapshots_by_user(self, uid):
        '''
        Returns the row of the matching snapshot entry or None if not in DB
        '''
        # Get current available_results
        print(f" getting snapshot by USER ID: {uid}")
        query = self.snapshots_table.select().where(
            and_(self.snapshots_table.c.uid == uid))
        connection = self.engine.connect()
        snaps = {}
        for snap_entry in connection.execute(query):
            snap_entry_dict = dict(snap_entry)
            snaps[snap_entry_dict['id']] = snap_entry_dict
        snaps = OrderedDict(sorted(snaps.items()))
        connection.close()
        return snaps

    def get_snapshot(self, uid, snapshot_id):
        '''
        Returns the row of the matching snapshot entry or None if not in DB
        '''
        # Get current available_results
        print(f" getting snapshot UID: {uid} , SNAP ID: {snapshot_id}")
        query = self.snapshots_table.select().where(
            and_(self.snapshots_table.c.uid == uid,
                 self.snapshots_table.c.id == snapshot_id))
        connection = self.engine.connect()
        match = connection.execute(query).fetchone()
        print(f"Finished getting snapshot : {match}")
        connection.close()
        return dict(match)

    def get_snapshot_by_time(self, uid, datetime):
        ''' Returns the row of the matching snapshot entry or None if not in DB '''
        # Get current available_results
        print(f" getting snapshot : {uid} - {datetime}")
        query = self.snapshots_table.select().where(
            and_(self.snapshots_table.c.uid == uid,
                 self.snapshots_table.c.datetime == datetime))
        connection = self.engine.connect()
        match = connection.execute(query).fetchone()
        print(f"Finished getting snapshot : {match}")
        connection.close()
        return match

    def get_parser_res(self, parser_name, snapshot_id):
        query = self.parsers_tables[parser_name].select().where(
            and_(self.parsers_tables[parser_name].c.snapshotid == snapshot_id))
        connection = self.engine.connect()
        match = connection.execute(query).fetchone()
        connection.close()
        return match.encoded_results
