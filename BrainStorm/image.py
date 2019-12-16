class image:
    def __init__(self,kind,h,w,data):
        self.kind = kind
        self.h = h
        self.w = w
        self.data = data
    def __repr__(self):
        return f'<Image: {self.kind} {self.h}x{self.w}>'
