import logging
log = logging.getLogger('game')

class GameShutdown(Exception):
    pass

import state
import event
def start():
    log.debug("Game starting")


    while state.running:
        if state.mode == 'title':
            event.fire('title.tick')
            
    return
