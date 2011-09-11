'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import term
import game

import logging
log = logging.getLogger('main')

def main():
    log.debug('Starting up')
    term.init()
    try:
        game.start()

    except game.GameShutdown:
        term.reset()
    except KeyboardInterrupt:
        term.reset()
        raise
    
    finally:
        log.debug('Shutting down')
        logging.shutdown()
        term.restore()
