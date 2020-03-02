class image:
    @classmethod
    def fromDict(cls,d):
        h = d["height"]
        w = d["width"]
        data = d["data"]
        return cls(h,w,data)
    def __init__(self,h,w,data):
        self.height = h
        self.width = w
        self.data = data
    def __repr__(self):
        return f'<Image: {self.height}x{self.width}>'
    def toDict(self):
            return {
                    "height":self.height,
                    "width":self.width,
                    "data":self.data
                    }
