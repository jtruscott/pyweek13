import logging
log = logging.getLogger('game')

class GameShutdown(Exception):
    pass

import state
import event
def start():
    log.debug("Game starting")

    state.new_state()
    state.mode = 'title'
    event.fire('%s.start' % state.mode)

    while state.running:
        try:
            event.fire('%s.tick' % state.mode)
            event.fire('%s.draw' % state.mode)
            event.fire('%s.prompt' % state.mode)
            event.fire('flip')
        except state.StateChanged:
            continue
    return

@event.on('ctrl-c')
def ctrlc():
    state.running = False
    raise GameShutdown()
