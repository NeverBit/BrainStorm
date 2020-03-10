import struct


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

    def send_message(self, data):
        # Append 'header': 4 bytes of length
        leng = len(data)
        header = struct.pack('!I', leng)
        data = header + data
        # Send final message
        leng += 4
        sent = 0
        curr_data = data
        while(sent != leng):
            temp = self.socket.send(data)
            sent += temp
            curr_data = curr_data[temp:]

    def receive_exact(self, size):
        size_left = size
        data = b''
        while(size_left != 0):
            temp_data = self.socket.recv(size_left)
            data += temp_data
            size_left -= len(temp_data)
            if(temp_data == b''):
                return b''
        return data

    def receive_message(self):
        # Start by reading 4 bytes of header
        header = self.receive_exact(4)
        if(header == b''):
            return b''
        payload_len, = struct.unpack('!I', header)
        return self.receive_exact(payload_len)

    def close(self):
        self.socket.close()

    def __enter__(self):
        return self

    def __exit__(self, ex, er, tb):
        self.close()
