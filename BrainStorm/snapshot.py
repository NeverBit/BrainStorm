from collections import namedtuple

Pose = namedtuple('translation','rotation')

class Snapshot:
    def __init__(self,time_ms,translation,rotation,col_img,dep_img,emotions):
        #epoch = dt.datetime.fromtimestamp(0)
        #self.datetime = epoch + dt.timedelta(milliseconds=time_ms)
        self.datetime = time_ms
        self.pose = Pose(translation, rotation)
        self.color_image = col_img
        self.depth_image = dep_img
        self.feelings = emotions
    def __repr__(self):
        return f'<{self.timestamp} {self.translation} {self.rotation} {self.col_img} {self.dep_img} {self.emotions}>'
