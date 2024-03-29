import event, state

import logging
log = logging.getLogger('term')

#are we on windows (wconio) or linux (curses)?
try:
    import WConio
    win = True
    log.debug("Imported WConio; win = %r", win)
    from term_win import *
    
except ImportError:
    import curses
    win = False
    log.debug("Imported curses; win = %r", win)
    try:
        from term_curses import *
    except ImportError:
        import sys
        print "This program requires either WConio or Curses!"
        sys.exit(1)


@event.on('setup')
def term_setup():
    log.debug("resizing to h=%r,w=%r", state.config.height, state.config.width)
    resize(state.config.height, state.config.width)

class BoxDouble:
    blank = ' '
    horiz = chr(0xCD)
    vert = chr(0xBA)
    tl = chr(0xC9)
    bl = chr(0xC8)
    tr = chr(0xBB)
    br = chr(0xBC)

class BoxSingle(BoxDouble):
    horiz = chr(0xC4)
    vert = chr(0xB3)
    tl = chr(0xDA)
    bl = chr(0xC0)
    tr = chr(0xBF)
    br = chr(0xD9)




class BoxMessage(BoxDouble):
    vert = chr(0xB3)
    tr = chr(0xB8)
    br = chr(0xBE)
    cur_top = chr(0xD1)
    cur_bottom = chr(0xCF)
    cur = chr(0xD8)

class Pointer:
    left = chr(0x10)
    right = chr(0x11)


class Room:
    player = chr(2)

event.on('flip')(flip)


def getkey():
    '''
        Get a key of keyboard input. Returns 1 character or the name of the special key.
        Some special keys are hijacked and get events fired instead.
    '''
    while True:
        key = raw_getkey()
        if key is None:
            continue
        if key in ['home', 'pgup', 'pgdn', 'end']:
            #message scroll
            if key == 'home': event.fire('scroll', home=True)
            if key == 'pgup': event.fire('scroll', rel= -1)
            if key == 'pgdn': event.fire('scroll', rel= 1)
            if key == 'end': event.fire('scroll', end=True)
        elif key == '\x03':
            #ctrl-c
            event.fire('ctrl-c')
        else:
            return key
