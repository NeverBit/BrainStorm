from connection import Connection
import socket

class Listener:
    def __init__(self,port,host='0.0.0.0',backlog=1000,reuseaddr=True):
        self.port = port
        self.host = host
        self.backlog = backlog
        self.reuseaddr = reuseaddr
    def __repr__(self):
        return f'Listener(port={self.port}, host=\'{self.host}\', backlog={self.backlog}, reuseaddr={self.reuseaddr})'
    def start(self):
        self.listener = socket.socket()
        if(self.reuseaddr):
            self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        ip_port_tup = (self.host,self.port)
        self.listener.bind(ip_port_tup)
        self.listener.listen(self.backlog)
    def stop(self):
        self.listener.close()
    def accept(self):
        try:
            client, c_address = self.listener.accept()
            return Connection(client)
        except:
            print("ERROR IN ACCEPT")
            raise Exception("exception in accept")
    def __enter__(self):
        self.start();
        return self
    def __exit__(self,ex,er,tb):
        self.stop()
