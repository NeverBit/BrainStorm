import socket
import struct
import time
from cli import CommandLineInterface

cli = CommandLineInterface()

@cli.command
def upload(address, user, thought):
    ip_port_list = address.split(':')
    ip_port_tup = (ip_port_list[0],int(ip_port_list[1]))
    soc = socket.socket()
    soc.connect(ip_port_tup)
    thought_bytes = thought.encode('utf8')
    time_val = int(time.time())
    user_id = int(user)
    packed = struct.pack('QQI',user_id,time_val,len(thought_bytes))
    packed = packed + thought_bytes
    soc.sendall(packed)
    soc.close()
    print('done')

if __name__ == '__main__':
    import sys
    sys.exit(cli.main())
