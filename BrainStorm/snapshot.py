
class Snapshot:
    def __init__(self,time_ms,translation,rotation,col_img,dep_img,emotions):
        #epoch = dt.datetime.fromtimestamp(0)
        #self.datetime = epoch + dt.timedelta(milliseconds=time_ms)
        self.timestamp = time_ms
        self.translation = translation
        self.rotation = rotation
        self.col_img = col_img
        self.dep_img = dep_img
        self.emotions = emotions
    def __repr__(self):
        return f'<{self.timestamp} {self.translation} {self.rotation} {self.col_img} {self.dep_img} {self.emotions}>'
