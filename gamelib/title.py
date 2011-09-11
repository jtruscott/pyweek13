import event, state

import logging
log = logging.getLogger('game')

@event.on('title.tick')
def tick():
    state.running = False
    return
