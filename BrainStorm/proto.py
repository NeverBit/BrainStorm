import io
import struct
from . import image as im


class Hello:
    def __init__(self,uid,uname,bday,gender):
        self.uid = uid
        self.uname = uname
        self.bday = bday
        self.gender = gender
    def serialize(self):
        encoded_name = self.uname.encode()
        data = struct.pack('!QI',self.uid,len(encoded_name))
        data += encoded_name
        data += struct.pack('!I',self.bday)
        data += self.gender.encode()
        return data
    def __repr__(self):
        return (f'<Hello; ID: {self.uid}, Name: {self.uname},'
                f'B-Day: {self.bday}, Gender: {self.gender}>')
    @classmethod
    def deserialize(cls,data):
        uid,enc_name_len = struct.unpack('!QI',data[:12])
        uname = data[12:12+enc_name_len].decode()
        bday,= struct.unpack('!I',data[12+enc_name_len:16+enc_name_len])
        gender = data[16+enc_name_len:].decode()
        return cls(uid,uname,bday,gender)


class Config:
    def __init__(self,supported_fields):
        self.supported_fields = supported_fields
    def serialize(self):
        data = struct.pack('!I',len(self.supported_fields))
        for field in self.supported_fields:
            enc_field = field.encode()
            data += struct.pack('!I',len(enc_field))
            data += enc_field 
        return data
    def __repr__(self):
        return f'<Config; Fields: {self.supported_fields}>'
    @classmethod
    def deserialize(cls,data):
        fields_count, = struct.unpack('!I',data[:4])
        fields = []
        offset = 4
        for i in range(0,fields_count):
            field_len, = struct.unpack('!I',data[offset:offset+4])
            offset += 4
            enc_field = data[offset:offset+field_len] 
            offset += field_len 
            fields.append( enc_field.decode())
        return cls(fields)




class Snapshot:
    def __init__(self,timestamp,translation,rotation,col_img,dep_img,feelings):
        print (' @@@ Debug initing proto snapshot msg ')
        self.timestamp = timestamp
        self.translation = translation
        self.rotation = rotation
        self.col_img = col_img
        self.dep_img = dep_img
        self.feelings = feelings
    def serialize(self):
        print (' @@@ Debug self serializing snapshot')
        data = struct.pack('!Qddd',self.timestamp,self.translation['x'],
                                                self.translation['y'],
                                                self.translation['z'])
        data += struct.pack('!dddd',self.rotation['x'],
                                    self.rotation['y'],
                                    self.rotation['z'],
                                    self.rotation['w'])
        data += struct.pack('!II',self.col_img.width,self.col_img.height)
        data += self.col_img.data
        data += struct.pack('!II',self.dep_img.width,self.dep_img.height)
        data += self.dep_img.data
        data += struct.pack('!ffff',*self.feelings)
        return data
    def __repr__(self):
        return (f'<Snapshot; Time: {self.timestamp}, Trans: {self.translation},'
                f'Rot: {self.rotation}, Col Img: {self.col_img.height}x{self.col_img.width}'
                f'Dep Img: {self.dep_img.height}x{self.dep_img.width}, Feels: {self.feelings}')
    @classmethod
    def deserialize(cls,data):
        offset = 0
        timestamp, = struct.unpack('!Q',data[offset:offset+8])
        offset += 8
        translation_raw = struct.unpack('!ddd',data[offset:offset+24])
        translation = {'x': translation_raw[0], 'y': translation_raw[1],
                        'z': translation_raw[2]}
        offset += 24
        rotation_raw = struct.unpack('!dddd',data[offset:offset+32])
        rotation = {'x': rotation_raw[0], 'y': rotation_raw[1],
                    'z': rotation_raw[2], 'w': rotation_raw[3]}
        offset += 32

        # Color Image
        col_img_w, col_img_h = struct.unpack('!II',data[offset:offset+8])
        offset += 8
        col_img_data = data[offset:offset + (3 * col_img_h * col_img_w)]
        col_img = im.image('Color',col_img_h,col_img_w,col_img_data)
        offset += 3 * col_img_h * col_img_w
        
        # Depth Image
        dep_img_data = data[offset:offset+8]
        print(f' @@@ Debug col_img_h * col_img_w = {col_img_h} {col_img_w}')
        print(f' @@@ Debug  dep_img_data len: {len(dep_img_data)}')
        print(f' @@@ Debug data len: {len(data)}')
        dep_img_w, dep_img_h = struct.unpack('!II',dep_img_data)
        offset += 8
        dep_img_data = data[offset:offset + (4 * dep_img_h * dep_img_w)]
        dep_img = im.image('Depth',dep_img_h,dep_img_w,dep_img_data)

        offset += 4 * dep_img_h * dep_img_w
        feelings = struct.unpack('!ffff',data[offset:offset+16])
        return cls(timestamp,translation,rotation,col_img,dep_img,feelings)
