import sys
import curses as C
import locale
locale.setlocale(locale.LC_ALL,"")

import logging
log = logging.getLogger('term.curses')
    
#import our color constants per-platform
#encode the bolditude in a bit curses coloring doesnt use, so we can keep it in a byte
HACK_BOLD = 0x8

BLACK = C.COLOR_BLACK
BLUE = C.COLOR_BLUE
GREEN = C.COLOR_GREEN
CYAN = C.COLOR_CYAN
RED = C.COLOR_RED
MAGENTA = C.COLOR_MAGENTA
BROWN = C.COLOR_YELLOW

LIGHTGRAY = LIGHTGREY = C.COLOR_WHITE
DARKGRAY = DARKGREY = C.COLOR_BLACK | HACK_BOLD
LIGHTBLUE = C.COLOR_BLUE | HACK_BOLD
LIGHTGREEN = C.COLOR_GREEN | HACK_BOLD
LIGHTCYAN = C.COLOR_CYAN | HACK_BOLD
LIGHTRED = C.COLOR_RED | HACK_BOLD
LIGHTMAGENTA = C.COLOR_MAGENTA | HACK_BOLD
YELLOW = C.COLOR_YELLOW | HACK_BOLD
WHITE = C.COLOR_WHITE | HACK_BOLD

def init():
    global scr
    scr = C.initscr()
    C.start_color()
    scr.keypad(False)
    C.noecho()

def uni(c):
    return c.decode('cp437').encode('utf-8')
#----------------------------------------------------------------------------
#Actual functions
all_dirty = False
def flip():
    '''
        Ensure the screen is up-to-date with any virtual shenanigans involved.
        Only needed by curses.
    '''
    scr.noutrefresh()
    C.doupdate()
    global all_dirty
    all_dirty = False

def reset():
    '''
        Reset the entire terminal.
        Used for things that want to exit the game cleanly.
    '''
    scr.erase()
    scr.refresh()

def resize(h, w):
    '''
        It's a little weird, but curses effectively demands an extra row and column
        or else you get "addstr() returned ERROR" nonesense.
        Sorry linux users!
    '''
    global MAX_X
    global MAX_Y
    MAX_X = w
    MAX_Y = h
    w = w + 1
    h = h + 1
    y,x = scr.getmaxyx()
    if y < h or x < w:
        raise Exception("Your window is x=%s, y=%s. Minimum required is x=%s, y=%s" % (x, y, w, h))
        C.resizeterm(h, w)
        scr.resize(h, w)
        
    
def restore():
    '''
        Keep the terminal usable.
        Always performed on exit.
    '''
    C.nocbreak()
    C.noraw()
    C.echo()
    scr.keypad(False)
    C.endwin()

def settitle(title):
    #gibberish, i tell you
    sys.stdout.write("\x1b]2;%s\x07" % title)

def setcursortype(i):
    C.curs_set(i)

color_pairs = {}
next_pair = 0
def get_color(fg, bg):
    global next_pair
    fg, bold = (fg & 0x7, fg & 0x8)
    bg = bg & 0x7
    if (fg, bg, bold) not in color_pairs:
        next_pair += 1
        #log.debug("creating pair %i: (%r, %r)", next_pair, fg, bg)
            
        #strip out hack_bold


        C.init_pair(next_pair, fg, bg)
        color_pair = C.color_pair(next_pair)
        if bold:
            color_pair |= C.A_BOLD
        
        color_pairs[(fg, bg, bold)] = color_pair

    return color_pairs[(fg, bg, bold)]
    
def draw_buffer(buf, x, y):
    if not buf.dirty:
        return
    global MAX_X, MAX_Y
    base_x = x
    for row in buf.data:
        x = base_x
        for fg, bg, ch in row[:buf.width]:
            color = get_color(fg, bg)
            ch = uni(ch)
            #log.debug("x: %r y: %r ch: %r, w: %r h: %r", x, y, ch, buf.width, buf.height)
            scr.addstr(y, x, ch, color)
            x += 1
            if x >= MAX_X:
                #log.debug("Breaking line early (%r >= %r)", x, MAX_X)
                break
        y += 1
        if y >= MAX_Y:
            #log.debug("Breaking draw early (%r >= %r)", y, MAX_Y)
            break
    return

ansiparse = None #we have to delay-load this thing
class KeyReader:
    """
        The fakest file-like object you ever did see.
    """
    def read(self, n):
        key = scr.getkey()
        log.debug("read %r", key)
        return key
    
def raw_getkey():
    global ansiparse
    if not ansiparse:
        import ansiparse as AP
        ansiparse = AP

    key = scr.getkey()
    log.debug("key is %r", key)
    if key == '\n':
        return 'enter'
    elif key == '\x1b':
        #ansi escape sequence, otherwise known as "ah crap"
        esc = ansiparse.parse_escape(KeyReader(), is_key=True)
        if esc.key is 'unknown':
            log.warn("Unknown ansi key! c: %r", esc.c)
            return None
        else:
            log.debug("ansi key is %r", esc.key)
            return esc.key
    if key == 'c':
        key = '\x03'
