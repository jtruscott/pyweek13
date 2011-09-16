import os, os.path
import screen, term

DEBUG = False
out = open('ansi.log', 'w')
def log(m):
    if not DEBUG:
        return
    out.write(m)
    out.write('\n')
    out.flush()

class Escape:
    meaning = None #ha!
    args = []
    key = None

color_map = {
    (0, 30): term.BLACK,
    (0, 31): term.RED,
    (0, 32): term.GREEN,
    (0, 33): term.BROWN,
    (0, 34): term.BLUE,
    (0, 35): term.MAGENTA,
    (0, 36): term.CYAN,
    (0, 37): term.LIGHTGREY,

    (1, 30): term.DARKGREY,
    (1, 31): term.LIGHTRED,
    (1, 32): term.LIGHTGREEN,
    (1, 33): term.YELLOW,
    (1, 34): term.LIGHTBLUE,
    (1, 35): term.LIGHTMAGENTA,
    (1, 36): term.LIGHTCYAN,
    (1, 37): term.WHITE,
}
last_color = 37
def lookup_color(bold, id=None):
    global last_color
    log('lookup: (%r,%r) lc %r' % (bold, id, last_color))
    if id is None:
        id = last_color
    elif id >= 40:
        id -= 10
    else:
        last_color = id
    color = color_map[(bold, id)]
    return color


#rrrgh global state
bold = 0

def parse_escape(f, is_key=False):
    """
        Parse an ANSI escape code.
        Return (some type of meaning, some values)
        Christ, I hate these things.
    """
    global bold
    ret = Escape()
    
    c = f.read(1)
    if c != '[':
        raise ValueError("Got %r, wanted [" % (c, chr))
    args = []
    arg = []
    def arg_or(idx, default):
        if len(args) > idx:
            return args[idx]
        return default

    def end_arg():
        if len(arg):
            arg_int = int(''.join(arg))
            args.append(arg_int)

    while True:
        c = f.read(1)
        if c not in '01234567890;':
            #we're done parsing numbers
            break
        if c == ';':
            #that's the end of an arg
            #make it an int instead of a string
            end_arg()
            arg = []
        else:
            #a number, oh boy
            arg.append(c)
    end_arg()
    ret.args = args
    #drawing escape sequences
    if c == 'C':
        #move
        ret.meaning = 'move_x'
        ret.x = arg_or(0, 1)
        ret.key = 'right'

    elif c == 'm':
        ret.meaning = 'color'
        ret.fg = None
        ret.bg = None
        for arg in args:
            if arg == 1:
                bold = 1
                ret.bold = True
                log("bolding")
                ret.fg = lookup_color(bold, None)
            if arg == 0:
                bold = 0
                log("un bolding")
                ret.fg = lookup_color(bold, None)
                ret.bg = term.BLACK
            if 30 <= arg <= 37:
                log("fg %r" % arg)
                ret.fg = lookup_color(bold, arg)
            if 40 <= arg <= 47:
                #bg colors 40-47 are the same as 30-37
                #oh, but backgrounds can't be bold. sorry.
                log("bg %r" % arg)
                ret.bg = lookup_color(0, arg)
    
    #key escape sequences
    elif c == 'A':
        ret.key = 'up'
    elif c == 'B':
        ret.key = 'down'
    elif c == 'D':
        ret.key = 'left'
    else:
        if is_key:
            ret.key = 'unknown'
            ret.c = c
        else:
            raise Exception(c)
    return ret

def read_to_buffer(f, width=80, max_height=None, crop=False):
    """
        if crop, kill rows at :width
        otherwise, let them wrap into new rows.
        we need both :(
    """
    rows = []
    row = []
    fg = term.WHITE
    bg = term.BLACK
    def add(c, _fg=None, _bg=None):
        if _fg is not None:
            f = _fg
        else:
            f = fg
        if _bg is not None:
            b = _bg
        else:
            b = bg
        #log("f: %r b: %r c: %r (%r)" % (f, b, c, hex(ord(c))))
        row.append([f, b, c])

    def finish_row():
        log("finishing row")
        while len(row) < width:
            add(' ')
        if crop:
            xrow = row[:width]
        else:
            xrow = row
        rows.append(xrow)
        fg = term.WHITE

    while True:
        c = f.read(1)
        if not c:
            break
        if c == chr(27): #esc
            esc = parse_escape(f)
            if esc.meaning == 'move_x':
                [add(' ', term.BLACK, term.BLACK) for x in range(esc.x)]

            elif esc.meaning == 'color':
                if esc.fg is not None:
                    fg = esc.fg
                if esc.bg is not None:
                    bg = esc.bg

        elif c in ('\r','\n'):
            finish_row()
            row = []
        else:
            add(c)
        if not crop and len(row) >= width:
            finish_row()
            row = []
    finish_row()
    if max_height:
        rows = rows[:max_height]
    buf = screen.Buffer(
        width=width, height=len(rows),
        data=rows
    )
    return buf

if __name__ == "__main__":
    import WConio as W
    x = 0
    def show(filename):
        global x
        f = open(filename)
        buf = read_to_buffer(f)
        buf.x = x
        x += buf.width
        buf.draw()
    try:
        import sys
        if not len(sys.argv) > 1:
            print "nom nom need argument"
        else:
            term.init()
            show(sys.argv[1])
            if len(sys.argv) > 2:
                show(sys.argv[2])
            term.flip()
        W.settitle("Mutants Of Melimnor")
        term.getkey()

    except:
        raise
    finally:
        W.textmode()
        W.textcolor(W.LIGHTGREY)
