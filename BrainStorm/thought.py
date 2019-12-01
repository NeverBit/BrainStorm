import struct
import datetime
import time
class Thought:
    def __init__(self,user_id,timestamp,thought):
        self.user_id = user_id
        self.timestamp = timestamp
        self.thought = thought
    def __repr__(self):
        return f'Thought(user_id={self.user_id}, timestamp={self.timestamp!r}, thought="{self.thought}")'
    def __str__(self):
        return f'[{self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}] user {self.user_id}: {self.thought}'
    def __eq__(self,other):
        if not  type(other) == Thought:
            return False
        return self.user_id == other.user_id and self.timestamp == other.timestamp and self.thought == other.thought
    def serialize(self):
        thought_bytes = self.thought.encode('utf8')
        time_val = int(self.timestamp.timestamp())
        user_id = int(self.user_id)
        packed = struct.pack('QQI',user_id,time_val,len(thought_bytes))
        packed = packed + thought_bytes
        return packed
    def deserialize(data):
        header = data[:20]
        (uid,time_val,t_length) = struct.unpack('QQI',header)
        thought = data[20:] 
        time = datetime.datetime.fromtimestamp(time_val)
        thoughtstr = thought.decode('utf8')
        return Thought(uid,time,thoughtstr)
