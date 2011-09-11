with open('debug.log', 'w') as dbglog:
    dbglog.write('')

import logging
logger = logging.getLogger('')
hdlr = logging.FileHandler('debug.log')
formatter = logging.Formatter('%(asctime)s %(name)s:%(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)
