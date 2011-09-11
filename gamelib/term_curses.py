import sys
import curses as C

import logging
log = logging.getLogger('term.curses')
    
#import our color constants per-platform
#encode the bolditude in a bit curses coloring doesnt use, so we can keep it in a byte
HACK_BOLD = 0x8

BLACK = curses.COLOR_BLACK
BLUE = curses.COLOR_BLUE
GREEN = curses.COLOR_GREEN
CYAN = curses.COLOR_CYAN
RED = curses.COLOR_RED
MAGENTA = curses.COLOR_MAGENTA
BROWN = curses.COLOR_YELLOW

LIGHTGRAY = LIGHTGREY = curses.COLOR_WHITE
DARKGRAY = DARKGREY = curses.COLOR_BLACK | HACK_BOLD
LIGHTBLUE = curses.COLOR_BLUE | HACK_BOLD
LIGHTGREEN = curses.COLOR_GREEN | HACK_BOLD
LIGHTCYAN = curses.COLOR_CYAN | HACK_BOLD
LIGHTRED = curses.COLOR_RED | HACK_BOLD
LIGHTMAGENTA = curses.COLOR_MAGENTA | HACK_BOLD
YELLOW = curses.COLOR_YELLOW | HACK_BOLD
WHITE = curses.COLOR_WHITE | HACK_BOLD

def init():
    global scr
    scr = C.initscr()
    C.start_color()
    scr.keypad(False)

#----------------------------------------------------------------------------
#Actual functions

def flip():
    '''
        Ensure the screen is up-to-date with any virtual shenanigans involved.
        Only needed by curses.
    '''
    C.doupdate()

def reset():
    '''
        Reset the entire terminal.
        Used for things that want to exit the game cleanly.
    '''
    scr.erase()
    scr.refresh()

def resize(h, w):
    y,x = W.getmaxyx()
    if y < h or x < w:
        raise Exception("Your window is x=%s, y=%s. Minimum required is x=%s, y=%s" % (x, y, w, h))
        curses.resizeterm(h, w)
        W.resize(h, w)
        
    
def restore():
    '''
        Keep the terminal usable.
        Always performed on exit.
    '''
    C.nocbreak()
    C.echo()
    scr.keypad(False)

def settitle(title):
    #gibberish, i tell you
    sys.stdout.write("\x1b]2;%s\x07" % title)

def setcursortype(i):
    C.curs_set(i)
