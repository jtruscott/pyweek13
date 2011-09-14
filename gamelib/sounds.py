try:
    import os
    import pyglet
    import threading
    nosound = False
except ImportError:
    nosound = True

import state, event

import logging
log = logging.getLogger('sound')

if nosound:
    log.debug("Sound disabled.")

media_cache = {}
loop = pyglet.app.EventLoop()
clk = pyglet.clock.get_default()

def play(name):
    if nosound or state.config.no_sound:
        return
    if name in media_cache:
        sound = media_cache[name]
    else:
        file_name = '%s.wav' % name
        log.debug("Loading sound: %r (%r)", name, file_name)
        sound = pyglet.resource.media(file_name, streaming=False)
        media_cache[name] = sound
    log.debug("Playing sound: %r", name)
    player = pyglet.media.ManagedSoundPlayer()
    player.queue(sound)
    player.play()

def start_pyglet():
    log.debug("Starting pyglet")
    while True:
        log.debug("tick")
        clk.tick()
    log.debug("Stopped pyglet")

@event.on('setup')
def setup_sound():
    background_thread = threading.Thread(target=start_pyglet)
    background_thread.daemon = True
    background_thread.start()
