with open('debug.log', 'w') as dbglog:
    dbglog.write('')

import logging
logger = logging.getLogger('')
hdlr = logging.FileHandler('debug.log')
formatter = logging.Formatter('%(asctime)s %(name)s:%(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

#we're using decorators, which run at file-load-time,
#so import all the modules we want in the right order
import event

import title
import message
import battle
