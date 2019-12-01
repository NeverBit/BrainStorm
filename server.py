import socket
import struct
import time
import threading
from pathlib import Path
from cli import CommandLineInterface

cli = CommandLineInterface()

files_lock = threading.Lock()

class Single_user_handler(threading.Thread):
    def __init__(self,client,data_dir):
        super().__init__()
        self.client = client
        self.data_dir = data_dir
    def run(self):
        while(1):
            bytes_to_read = 20;
            header = b''
            while(bytes_to_read > 0):
                recieved = self.client.recv(bytes_to_read)
                if(recieved == b''):
                    self.client.close()
                    return
                header = header + recieved
                bytes_to_read = 20 - len(header)
            (uid,time_val,t_length) = struct.unpack('QQI',header)
            bytes_to_read = t_length
            thought = b'' 
            while(bytes_to_read > 0):
                part = self.client.recv(bytes_to_read)
                if(part == b''):
                    self.client.close()
                    return
                thought = thought + part
                bytes_to_read = bytes_to_read - len(part)
            time_str = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(time_val))
            thought = thought.decode('utf8')
            # Writing to file
            files_lock.acquire()
            dd_path = Path(self.data_dir)
            dd_path.mkdir(exist_ok=True)
            u_path = dd_path / '{0}'.format(uid)
            u_path.mkdir(exist_ok=True)
            sec_path = u_path / '{0}.txt'.format(time_str)
            file_already_existed = sec_path.exists()
            with sec_path.open('a') as sec_file:
                if(file_already_existed):
                    sec_file.write('\n')
                sec_file.write(thought)
            files_lock.release()

@cli.command
def run(address,data):
    ip_port_list = address.split(':')
    ip_port_tup = (ip_port_list[0],int(ip_port_list[1]))
    data_dir = data # Just because 'data' is a bad argument name
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

if __name__ == '__main__':
    import sys
    sys.exit(cli.main())
