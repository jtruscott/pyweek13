import os, os.path
import screen, term

class Escape:
    meaning = None #ha!
    args = []

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
def lookup_color(bold, id):
    return color_map[(bold, id)]


#rrrgh global state
bold = 0

def parse_escape(f):
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
    if c == 'C':
        #move
        ret.meaning = 'move_x'
        ret.x = arg_or(0, 1)

    elif c == 'm':
        ret.meaning = 'color'
        ret.fg = None
        ret.bg = None
        for arg in args:
            if arg == 1:
                bold = True
                ret.bold = True
            if arg == 0:
                bold = False
                ret.fg = term.WHITE
                ret.bg = term.BLACK
            if 30 <= arg <= 37:
                ret.fg = lookup_color(bold, arg)
            if 40 <= arg <= 47:
                #bg colors 40-47 are the same as 30-37
                #oh, but backgrounds can't be bold. sorry.
                ret.bg = lookup_color(0, arg-10)
    else:
        raise Exception(c)
    return ret

def read_to_buffer(f, width=80, max_height=None):
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
        row.append([f, b, c])

    def finish_row():
        while len(row) < width:
            add(' ')
        rows.append(row)
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
    try:
        import sys
        if not len(sys.argv) > 1:
            path = os.path.join('..', 'data', 'maps', 'test.ans')
        else:
            path = sys.argv[1]
        f = open(path)
        term.init()
        buf = read_to_buffer(f)
        buf.draw()
        term.flip()

    except:
        W.textmode()
        raise
    finally:
        W.textcolor(W.LIGHTGREY)
