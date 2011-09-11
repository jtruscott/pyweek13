import event
from player import Player

import logging
log = logging.getLogger('state')

mode = "title"
running = True
class config:
    #configuration defaults, overridden by config.json
    width = 120
    height = 60

#the game's player
player = None


@event.on('setup')
def load_config():
    import os, json
    config_filename = 'config.json'

    if os.path.exists(config_filename):
        log.debug('Loading config file %s', config_filename)
        
        config_data = json.loads(open(config_filename))
        for key, value in config_data.items():
            setattr(config, key, value)
    else:
        log.debug('No config file exists; using default settings')

def new_state():
    global player
    player = Player()

def load_state():
    pass
def save_state():
    pass
