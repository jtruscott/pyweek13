import term

class Buffer:
    """
        A buffer on the screen.
        Can have relatively-positioned children.
        Data is:
            a list, of length height,
            of lists, of length width,
            of (fg, bg, character) tuples.
    """
    def __init__(self, width, height, data, x=0, y=0, children=None):
        self.width = width
        self.height = height
        self.data = data
        self.dirty = True
        self.x = x
        self.y = y
        self.children = children or []

    def draw(self, xoff=0, yoff=0):
        #xoff and yoff are screen offsets from our parent.
        xoff = xoff + self.x
        yoff = yoff + self.y

        #put ourselves on the screen
        term.draw_buffer(self, xoff, yoff)

        #have our children do similar
        for child in self.children:
            child.draw(xoff, yoff)

class Text(Buffer):
    def __init__(self, message, fg=term.WHITE, bg=term.BLACK, center_to=None, **kwargs):
        self.message = self.base_message = message
        self.fg = fg
        self.bg = bg
        self.center_to = center_to

        Buffer.__init__(self, width=0, height=1, data=None, **kwargs)
        self.update_data()

    def set(self, message):
        self.message = message
        self.update_data()
    
    def format(self, fmt):
        self.message = self.base_message % fmt
        self.update_data()

    def update_data(self):
        data = []
        msg = self.message
        if self.center_to:
            msg = msg.center(self.center_to)
        for c in msg:
            data.append((self.fg, self.bg, c))
        self.width = len(data)
        self.data = [data]
        self.dirty = True


#----------------------------------------------------------------------

def make_box(width, height, x=0, y=0,
            border_fg=term.WHITE, border_bg=term.BLACK,
            interior_fg=term.WHITE, interior_bg=term.BLACK,
            boxtype=term.BoxDouble,
            draw_top=True, draw_bottom=True):
    data = []
    (blank, horiz, vert, tl, tr, bl, br) = (boxtype.blank, boxtype.horiz, boxtype.vert, boxtype.tl, boxtype.tr, boxtype.bl, boxtype.br)
    
    mid_rows = height
    if draw_top:
        mid_rows -= 1
        data.append([(border_fg, border_bg, tl)] + ([(border_fg, border_bg, horiz)]*(width-2)) + [(border_fg, border_bg, tr)])

    if draw_bottom:
        mid_rows -= 1

    for row in range(mid_rows):
        data.append([(border_fg, border_bg, vert)] + ([(interior_fg, interior_bg, blank)]*(width-2)) + [(border_fg, border_bg, vert)])

    if draw_bottom:
        data.append([(border_fg, border_bg, bl)] + ([(border_fg, border_bg, horiz)]*(width-2)) + [(border_fg, border_bg, br)])
    


    buf = Buffer(width=width, height=height, data=data, x=x, y=y)
    return buf
