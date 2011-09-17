import os, os.path
import event, state, ansiparse, term

import logging
log = logging.getLogger('game')


x = 0
@event.on('title.start')
def title_start():
    global left, right
    def open_file(filename):
        global x
        f = open(filename)
        buf = ansiparse.read_to_buffer(f)
        buf.x = x
        x += buf.width
        return buf
    left = open_file(os.path.join('data','Melimnor1'))
    right = open_file(os.path.join('data','Melimnor2'))
    
@event.on('title.draw')
def title_draw():
    left.draw()
    right.draw()

@event.on('title.prompt')
def title_prompt():
    while True:
        c = term.getkey()
        if c == 'enter':
            event.fire('explore.start')
            state.mode = 'explore'
            raise state.StateChanged()


@event.on('defeat.start')
def start_defeat():
    pass
@event.on('defeat.prompt')
def defeat_prompt():
    import message
    key = term.getkey()
    if key == 'down':
        message.scroll_message(rel=-1)
    if key == 'up':
        message.scroll_message(rel=1)
        
