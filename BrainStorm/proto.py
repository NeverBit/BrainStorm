from collections import namedtuple
import io
import json
import struct
from . import image as im


Pose = namedtuple('Pose', ('translation', 'rotation'))


class Snapshot:
    '''
    Represents a complete snapshot, including the binary parts (images)
    '''

    def __init__(
            self,
            uid,
            datetime,
            translation,
            rotation,
            col_img,
            dep_img,
            feelings):
        self.uid = uid
        self.datetime = datetime
        self.pose = Pose(translation, rotation)
        self.col_img = col_img
        self.dep_img = dep_img
        self.feelings = feelings

    def toDict(self):
        return {
            'uid': self.uid,
            'datetime': self.datetime,
            'pose': {
                'translation': self.pose.translation,
                'rotation': self.pose.rotation
            },
            'color_image': self.col_img.toDict(),
            'depth_image': self.dep_img.toDict(),
            'feelings': self.feelings
        }

    def __repr__(self):
        return (
            f'<Snapshot; Time: {self.datetime}, Trans: {self.pose.translation}, '
            f'Rot: {self.pose.rotation}, Col Img: {self.col_img.height}x{self.col_img.width}, '
            f'Dep Img: {self.dep_img.height}x{self.dep_img.width}, Feels: {self.feelings}')

    @classmethod
    def fromDict(cls, d):
        uid = d['uid']
        ts = d['datetime']
        trans = d['pose']['translation']
        rot = d['pose']['rotation']
        col_img = im.image.fromDict(d['color_image'])
        dep_img = im.image.fromDict(d['depth_image'])
        fee = d['feelings']
        return cls(uid, ts, trans, rot, col_img, dep_img, fee)


class UserInfo:
    def __init__(self, uid, name, bday, gender):
        self.uid = uid
        self.name = name
        self.bday = bday
        self.gender = gender

    def toDict(self):
        return {'uid': self.uid,
                'name': self.name,
                'bday': self.bday,
                'gender': self.gender
                }

    def __repr__(self):
        return (
            f'<UserInfo; Id: {self.uid}, Name: {self.name}, Birthday: {self.bday}, '
            f'Gender: {self.gender}>')

    @classmethod
    def fromDict(cls, d):
        uid = d['uid']
        name = d['name']
        bday = d['bday']
        gender = d['gender']
        return cls(uid, name, bday, gender)


class SnapshotSlim:
    '''
    Represents a partial snapshot, excluding the binary parts (images)
    '''

    def __init__(
            self,
            user_info,
            datetime,
            translation,
            rotation,
            col_img_path,
            dep_img_path,
            feelings):
        self.user_info = user_info
        self.datetime = datetime
        self.pose = Pose(translation, rotation)
        self.col_img_path = col_img_path
        self.dep_img_path = dep_img_path
        self.feelings = feelings

    def toDict(self):
        return {
            'user_info': self.user_info.toDict(),
            'datetime': self.datetime,
            'pose': {
                'translation': self.pose.translation,
                'rotation': self.pose.rotation
            },
            'color_image_path': self.col_img_path,
            'depth_image_path': self.dep_img_path,
            'feelings': self.feelings
        }

    def __repr__(self):
        return (
            f'<SnapshotSlim; user_info: {self.user_info}, Time: {self.datetime}, Trans: {self.pose.translation}, '
            f'Rot: {self.pose.rotation}, Col Img Path: {self.col_img_path}, '
            f'Dep Img Path: {self.dep_img_path}, Feels: {self.feelings}>')

    @classmethod
    def fromDict(cls, d):
        user_info = UserInfo.fromDict(d['user_info'])
        ts = d['datetime']
        trans = d['pose']['translation']
        rot = d['pose']['rotation']
        col_img_path = d['color_image_path']
        dep_img_path = d['depth_image_path']
        fee = d['feelings']
        return cls(user_info, ts, trans, rot, col_img_path, dep_img_path, fee)
