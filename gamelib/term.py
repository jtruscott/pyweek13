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
    from term_curses import *

@event.on('setup')
def term_setup():
    log.debug("resizing to h=%r,w=%r", state.config.height, state.config.width)
    resize(state.config.height, state.config.width)
