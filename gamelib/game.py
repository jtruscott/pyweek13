import logging
log = logging.getLogger('game')

class GameShutdown(Exception):
    pass

def start():
    log.debug("Game starting")
    return
