from . import parsers
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, BigInteger, String, ForeignKey, and_

parsers_names = list(parsers.registered_parsers.keys())

class DbBase:
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

        self.parsers_tables = {}
        for parser in parsers_names:    
            self.parsers_tables[parser] = Table(
                parser, meta, 
                Column('id', Integer, primary_key = True), 
                Column('snapshotid', Integer, ForeignKey('snapshots.id')),
                Column('encoded_results', String, nullable=False), 
            )

        meta.create_all(self.engine)



class Reader(DbBase):
    def __init__(self,database_url):
        DbBase.__init__(self,database_url)

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


    def get_user(self,uid):
        '''  Get a single user from the DB'''
        query = self.users_table.select().where(and_(self.users_table.c.id == uid))
        connection = self.engine.connect()
        found = connection.execute(query).fetchone()
        print(f"Finished getting user : {found}")
        connection.close()
        if not found:
            return None
        return dict(found)


    def get_snapshots_by_user(self,uid):
        ''' Returns the row of the matching snapshot entry or None if not in DB '''
        # Get current available_results
        print(f" getting snapshot by USER ID: {uid}")
        query = self.snapshots_table.select().where(
                        and_(self.snapshots_table.c.uid == uid))
        connection = self.engine.connect()
        snaps = {}
        for entry in connection.execute(query):
            print(f" iterating snapshot: {entry}, {dict(entry)}")
            entryDict = dict(entry)
            snaps[entryDict['id']] = entryDict
        connection.close()
        return snaps


    def get_snapshot(self,uid,snapshotid):
        ''' Returns the row of the matching snapshot entry or None if not in DB '''
        # Get current available_results
        print(f" getting snapshot UID: {uid} , SNAP ID: {snapshotid}")
        query = self.snapshots_table.select().where(
                        and_(self.snapshots_table.c.uid == uid,
                             self.snapshots_table.c.id == snapshotid))
        connection = self.engine.connect()
        match = connection.execute(query).fetchone()
        print(f"Finished getting snapshot : {match}")
        connection.close()
        return dict(match)

    def get_parser_res(self,parser_name,snapshotid):
        query = self.parsers_tables[parser_name].select().where(
                        and_(self.parsers_tables[parser_name].c.snapshotid == snapshotid))
        connection = self.engine.connect()
        match = connection.execute(query).fetchone()
        print(f"Finished getting parser res : {match}")
        connection.close()
        return match.encoded_results
