import struct
from .image import image
from .proto import Snapshot
from .cortex_pb2 import User as UserPb
from .cortex_pb2 import Snapshot as SnapshotPb


# Store of supported readers,
# accessible by the version number
readersStore = {}


def get_reader(versionNum):
    '''
    Get a .mind file reader for a specific
    format version number
    '''
    return readersStore[versionNum]


def reader(versionNum):
    '''
    A wrapper to allow automatic registeration
    of different .mind reader classes
    '''
    def wrapper(clss):
        readersStore[versionNum] = clss
        return clss
    return wrapper


@reader(1)
class reader_v1:
    '''
    Read old-format binary mind files
    '''
    def __init__(self, mindStream):
        self.file = mindStream
        # Reading header
        self.uid, = struct.unpack('Q', self.file.read(8))
        nameLen, = struct.unpack('I', self.file.read(4))
        self.uname = self.file.read(nameLen).decode('ascii')
        self.bday, = struct.unpack('I', self.file.read(4))
        self.gender = self.file.read(1).decode('ascii')

    def read_snapshot(self):
        # Time, Translation, Rotation
        data = self.file.read(64)
        if (data == b''):
            return None
        time, trans_x, trans_y, trans_z, = struct.unpack(
            'Qddd', data[:32])
        rot_x, rot_y, rot_z, rot_w = struct.unpack(
            'dddd', data[32:])
        translation = {'x': trans_x, 'y': trans_y, 'z': trans_z}
        rotation = {'x': rot_x, 'y': rot_y, 'z': rot_z, 'w': rot_w}
        # Color Image
        col_h, col_w = struct.unpack('II', self.file.read(8))
        # Fixing BGR to RGB

        def bgr_reader():
            for i in range(0, col_h * col_w * 3, 3):
                bgr_trio = self.file.read(3)
                yield bgr_trio[::-1]
        img_rgb = b''.join(bgr_reader())
        color_img = image(col_h, col_w, img_rgb)
        # Depth Image
        dep_h, dep_w = struct.unpack('II', self.file.read(8))
        img_dep = self.file.read(dep_h * dep_w * 4)
        dep_img = image(dep_h, dep_w, img_dep)
        # Emotions
        hunger, thirst, exha, happy = struct.unpack('ffff', self.file.read(16))
        emotions = (hunger, thirst, exha, happy)
        return Snapshot(
            self.uid,
            time,
            translation,
            rotation,
            color_img,
            dep_img,
            emotions)


@reader(2)
class reader_v2:
    '''
    Read protobuf-based mind files
    '''
    def __init__(self, mindStream):
        self.file = mindStream

        # Reading header
        buf = self.file.read(4)
        if not buf:
            return
        userLen, = struct.unpack('I', buf)
        buf = self.file.read(userLen)
        if not buf:
            return
        user = UserPb()
        user.ParseFromString(buf)

        self.uid = user.user_id
        self.uname = user.username
        self.bday = user.birthday
        if (user.gender == 0):
            self.gender = 'm'
        elif (user.gender == 1):
            self.gender = 'f'
        else:
            self.gender = 'o'

    def read_snapshot(self):
        buf = self.file.read(4)
        if not buf:
            return

        snapLen, = struct.unpack('I', buf)
        buf = self.file.read(snapLen)
        if not buf:
            return
        snap = SnapshotPb()
        snap.ParseFromString(buf)

        col_img = snap.color_image
        col_img = image(col_img.height, col_img.width, col_img.data)
        dep_img = snap.depth_image
        # Converting PB's 'Repeated Scalar Container' to a list
        dep_img_data = dep_img.data[:]
        dep_img = image(dep_img.height, dep_img.width, dep_img_data)

        return Snapshot(self.uid, snap.datetime,
                        snap.pose.translation, snap.pose.rotation,
                        col_img, dep_img,
                        snap.feelings)
