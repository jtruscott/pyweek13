import term as T

class Buffer:
    def __init__(self, width, height, data, x=0, y=0, children=None):
        self.width = width
        self.height = height
        self.data = data
        self.dirty = True
        self.x = x
        self.y = y
        self.children = children or []

    
    def dirty(self):
        self.dirty = True

    def draw(self, xoff=None, yoff=None):
        #xoff and yoff are screen offsets from our parent.
        if xoff is None:
            xoff = self.x
        if yoff is None:
            yoff = self.x

        #put ourselves on the screen

        #have our children do such things
        for child in self.children:
            child.draw(self.x + xoff, self.y + yoff)
