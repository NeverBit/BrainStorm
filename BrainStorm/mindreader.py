import datetime as dt
import struct
from .image import image
from .snapshot import Snapshot
from .cortex_pb2 import User as UserPb
from .cortex_pb2 import Snapshot as SnapshotPb


readersStore = {}


def get_reader(versionNum):
    return readersStore[versionNum]


def reader(versionNum):
    def wrapper(clss):
        readersStore[versionNum] = clss
        return clss
    return wrapper


@reader(1)
class reader_v1:
    def __init__(self,mindStream):
        self.file = mindStream 
        # Reading header
        self.uid, = struct.unpack('Q',self.file.read(8))
        nameLen, = struct.unpack('I',self.file.read(4))
        self.uname = self.file.read(nameLen).decode('ascii')
        self.bday, =  struct.unpack('I',self.file.read(4))
        self.gender = self.file.read(1).decode('ascii')

    def read_snapshot(self):
        # Time, Translation, Rotation
        data = self.file.read(64)
        if (data == b''):
            return None
        time, trans_x,trans_y,trans_z,rot_x,rot_y,rot_z,rot_w = struct.unpack('Qddddddd',data)
        translation = {'x':trans_x,'y':trans_y,'z':trans_z}
        rotation = {'x':rot_x,'y':rot_y,'z':rot_z,'w':rot_w}
        # Color Image
        col_h,col_w = struct.unpack('II',self.file.read(8))
        # Fixing BGR to RGB
        def bgr_reader():
            for i in range(0,col_h*col_w*3,3):
                bgr_trio = self.file.read(3)
                yield bgr_trio[::-1]
        img_rgb = b''.join(bgr_reader())
        color_img = image('Color',col_h,col_w,img_rgb)
        # Depth Image
        dep_h,dep_w = struct.unpack('II',self.file.read(8))
        img_dep = self.file.read(dep_h * dep_w * 4)
        dep_img = image('Depth',dep_h,dep_w,img_dep)
        # Emotions
        hunger, thirst, exha, happy = struct.unpack('ffff',self.file.read(16))
        emotions = (hunger,thirst,exha,happy)
        return SnapshotBinary(time, translation, rotation,color_img,dep_img,emotions)


@reader(2)
class reader_v2:
    def __init__(self,mindStream):
        self.file = mindStream
        # Reading header
        userLen, = struct.unpack('I',self.file.read(4))
        print(f'user len: {userLen}')
        user = UserPb()
        user.ParseFromString(self.file.read(userLen))

        self.uid = user.user_id 
        self.uname = user.username
        self.bday = user.birthday
        if (user.gender == 0):
            self.gender = 'm' 
        elif  (user.gender == 1):
            self.gender = 'f'
        else:
            self.gender = 'o'
        
    def read_snapshot(self):
        snapLen, = struct.unpack('I',self.file.read(4))
        print(f'snap len: {snapLen}')
        snap = SnapshotPb()
        snap.ParseFromString(self.file.read(snapLen))
        return snap
