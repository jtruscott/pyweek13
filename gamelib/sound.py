try:
    import pygame
    nosound = False
except ImportError:
    nosound = True

import state, event
import os, time

import logging
log = logging.getLogger('sound')

if nosound:
    log.debug("Sound disabled.")

sound_cache = {}
channels = {}

def play(name, channel="misc", wait=False):
    if nosound or state.config.no_sound:
        return
    if channel not in channels:
        channels[channel] = pygame.mixer.find_channel()

    if name in sound_cache:
        sound = sound_cache[name]
    else:
        file_name = os.path.join('data','%s.wav' % name)
        log.debug("Loading sound: %r (%r)", name, file_name)
        sound = pygame.mixer.Sound(file_name)
        sound_cache[name] = sound
    
    log.debug("Playing sound '%r' on channel '%r'", name, channel)
    channels[channel].play(sound)
    if wait:
        time.sleep(sound.get_length())

@event.on('setup')
def setup_sound():
    if nosound or state.config.no_sound:
        return
    #witchcraft, this one
    pygame.mixer.pre_init(44100,-16,2, 1024)
    pygame.mixer.init()
