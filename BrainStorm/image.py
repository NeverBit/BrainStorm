class image:
    '''
    Represents and image in a snapshot
    '''
    @classmethod
    def fromDict(cls, d):
        '''
        Parses an image from a dictionary
        '''
        h = d["height"]
        w = d["width"]
        data = d["data"]
        return cls(h, w, data)

    def __init__(self, h, w, data):
        self.height = h
        self.width = w
        self.data = data

    def __repr__(self):
        return f'<Image: {self.height}x{self.width}>'

    def toDict(self):
        '''
        Encodes the image into a dictionary
        '''
        return {
            "height": self.height,
            "width": self.width,
            "data": self.data
        }
