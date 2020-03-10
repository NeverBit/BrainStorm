class Connection:
    @classmethod
    def connect(cls, ip, port):
        ip_port_tup = (ip, port)
        soc = socket.socket()
        soc.connect(ip_port_tup)
        return Connection(soc)

    def __init__(self, socket):
        self.socket = socket

    def __repr__(self):
        me = self.socket.getsockname()
        other = self.socket.getpeername()
        return f'<Connection from {me[0]}:{me[1]} to {other[0]}:{other[1]}>'

    def send(self, data):
        leng = len(data)
        sent = 0
        curr_data = data
        while(leng != sent):
            temp = self.socket.send(data)
            sent += temp
            curr_data[sent:]

    def receive(self, size):
        size_left = size
        data = b''
        while(size_left != 0):
            temp_data = self.socket.recv(size_left)
            data += temp_data
            size_left -= len(temp_data)
            if(temp_data == b''):
                raise Exception("Connection Closed")
        return data

    def close(self):
        self.socket.close()

    def __enter__(self):
        return self

    def __exit__(self, ex, er, tb):
        self.close()
