from collections import namedtuple
import io
import json
import struct
from . import image as im


Pose = namedtuple('Pose' ,('translation','rotation'))

class Snapshot:
    def __init__(self,timestamp,translation,rotation,col_img,dep_img,feelings):
        self.timestamp = timestamp
        self.pose = Pose(translation, rotation)
        self.col_img = col_img
        self.dep_img = dep_img
        self.feelings = feelings
    def toDict(self):
            return {
                    "timestamp":self.timestamp,
                    "pose":{
                            "translation":self.pose.translation,
                            "rotation":self.pose.rotation
                            },
                    "color_image":self.col_img.toDict(),
                    "depth_image":self.dep_img.toDict(),
                    "emotions":self.feelings
                    }
    def __repr__(self):
        return (f'<Snapshot; Time: {self.timestamp}, Trans: {self.pose.translation},'
                f'Rot: {self.pose.rotation}, Col Img: {self.col_img.height}x{self.col_img.width}'
                f'Dep Img: {self.dep_img.height}x{self.dep_img.width}, Feels: {self.feelings}')
    @classmethod
    def fromDict(cls,d):
        ts = d["timestamp"]
        trans = d["pose"]["translation"]
        rot = d["pose"]["rotation"]
        col_img = im.image.fromDict(d["color_image"],"Color")
        dep_img = im.image.fromDict(d["depth_image"],"Depth")
        fl = d["emotions"]
        return cls(ts,trans,rot,col_img,dep_img,fl)
