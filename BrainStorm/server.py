import socket
import struct
import time
import threading
from pathlib import Path
from .connection import Connection
from .proto import Hello,Config
from .proto import Snapshot as SnapshotMsg
from . import parsers
from . import proto


files_lock = threading.Lock()


parsers_list = parsers.registered_parsers
parsers_names = list(parsers_list.keys())

class parser_context:
    def __init__(self,save_dir):
        self.dir = save_dir

class Single_user_handler(threading.Thread):
    def __init__(self,client,data_dir):
        super().__init__()
        self.client = client
        self.connection = Connection(client)
        self.data_dir = data_dir
    def run(self):
        # Reading 'Hello'
        raw_hello = self.connection.receive_message()
        if raw_hello == b'':
            self.client.close()
            # User disconnected prematurely
            return
        hello_msg = Hello.deserialize(raw_hello)
        
        # Sendeing 'Config'
        conf = Config(parsers_names)
        self.connection.send_message(conf.serialize())

        # Reading 'Snapshot'
        raw_snap = self.connection.receive_message()
        if raw_snap == b'':
            print('User disconnected prematurely')
            self.client.close()
            # User disconnected prematurely
            return
        snap_msg = SnapshotMsg.deserialize(raw_snap)

        # Make user & time directories
        dd_path = Path(self.data_dir)
        dd_path.mkdir(exist_ok=True)
        user_path = dd_path / f'{hello_msg.uid}'
        user_path.mkdir(exist_ok=True)
        datetime_path = user_path / f'{snap_msg.timestamp}'
        datetime_path.mkdir(exist_ok=True)
        
        # Create context for parsers
        p_context = parser_context(datetime_path)
        for parser in parsers_list.values():
            parser(p_context,snap_msg)

def run_server(address,port,data_dir):
    ip_port_tup = (address,port)
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    listener.bind(ip_port_tup)
    listener.listen(100)
    while(1):
        try:
            client, c_address = listener.accept()
        except:
            print("ERROR IN ACCEPT")
            raise exception("exception in accept")
        handler = Single_user_handler(client,data_dir)
        handler.start()
