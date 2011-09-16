'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import term
import event
import game

import logging
log = logging.getLogger('main')

def main():
    log.debug('Starting up')
    term.init()
    term.settitle('Mutants Of Melimnor    (PyWeek #13: Mutate!)')
    try:
        event.fire('setup')
        game.start()

    except game.GameShutdown:
        term.reset()
    except KeyboardInterrupt:
        term.reset()
        raise
    except Exception, e:
        log.exception(e)
        raise

    finally:
        log.debug('Shutting down')
        logging.shutdown()
        term.restore()
