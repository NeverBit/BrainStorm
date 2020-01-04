class image:
    @classmethod
    def fromDict(cls,d,kind):
        h = d["height"]
        w = d["width"]
        data = d["data"]
        return cls(kind,h,w,data)
    def __init__(self,kind,h,w,data):
        self.kind = kind
        self.height = h
        self.width = w
        self.data = data
    def __repr__(self):
        return f'<Image: {self.kind} {self.h}x{self.w}>'
    def toDict(self):
            print(' @@@ DEBUG in image toDict')
            return {
                    "height":self.height,
                    "width":self.width,
                    "data":self.data
                    }
