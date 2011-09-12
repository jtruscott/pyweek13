import logging
log = logging.getLogger('game')

class GameShutdown(Exception):
    pass

import state
import event
def start():
    log.debug("Game starting")

    state.new_state()
    state.mode = 'battle'

    while state.running:
        event.fire('%s.tick' % state.mode)
        event.fire('%s.draw' % state.mode)
        event.fire('%s.prompt' % state.mode)
        event.fire('flip')
    return

@event.on('ctrl-c')
def ctrlc():
    state.running = False
    raise GameShutdown()
