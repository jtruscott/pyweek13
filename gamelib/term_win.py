import WConio as W

import logging
log = logging.getLogger('term.windows')

#import our color constants per-platform
BLACK = 0
BLUE = 1
GREEN = 2
CYAN = 3
RED = 4
MAGENTA = 5
BROWN = 6
LIGHTGRAY = LIGHTGREY = 7
DARKGRAY = DARKGREY = 8
LIGHTBLUE = 9
LIGHTGREEN = 10
LIGHTCYAN = 11
LIGHTRED = 12
LIGHTMAGENTA = 13
YELLOW = 14
WHITE = 15

defaultcolor = W.gettextinfo()[4]
def init():
    W.textmode()
    setcursortype(0)



#----------------------------------------------------------------------------
#Actual functions

def flip():
    '''
        Ensure the screen is up-to-date with any virtual shenanigans involved.
        Only needed by curses.
    '''
    pass

def reset():
    '''
        Reset the entire terminal.
        Used for things that want to exit the game cleanly.
    '''
    W.textmode()

def resize(h, w):
    import subprocess
    subprocess.call(['mode', 'con', 'lines=%i' % h, 'cols=%i' % w], shell=True)
    #subprocess.call(["mode", "con", "cp", "select=437"], shell=True)
    #since we have subprocess already here... this is as good a place as any to set the 437 codepage.
    #commented out because I'm not confident it does anything, but if we find out we do need it, it's here.
        
    
def restore():
    '''
        Keep the terminal usable.
        Always performed on exit.
    '''
    W.clreol()
    W.textattr(defaultcolor)
    W.setcursortype(1)

def settitle(title):
    W.settitle(title)

def setcursortype(i):
    W.setcursortype(i)

def draw_buffer(buf, x, y):
    if buf.dirty:
        #generate a wconio buffer
        buf._text = render_buffer(buf)
        buf.dirty = False
    
    W.puttext(x, y,
            x + buf.width-1,
            y + buf.height-1,
            buf._text
    )

def render_buffer(buf):
    text = []
    for row in buf.data:
        for fg, bg, ch in row[:buf.width]:
             color = chr(fg + (bg << 4))
             text.append(ch)
             text.append(color)
    #log.debug('text: %r', text)
    return ''.join(text)

def raw_getkey():
    key = W.getkey()
    if key in ('\r', '\n'):
        key = 'enter'
        
    return key
