import logging
log = logging.getLogger('game')

class GameShutdown(Exception):
    pass

import state
import event
def start():
    log.debug("Game starting")

    state.new_state()
    state.mode == 'battle'

    while state.running:
        if state.mode == 'title':
            event.fire('title.tick')
        if state.mode == 'battle':
            event.fire('battle.tick')
    return
