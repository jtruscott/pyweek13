import event, message, term, state, screen, room

import logging
log = logging.getLogger('explore')
class level:
    room = None
    input_mode = 'level'

@event.on('setup')
def setup_explore_ui():

    global action_zone, viewport
    conf = state.config
    action_height = conf.height - conf.viewport_height
    action_zone = screen.make_box(conf.width, action_height,
                                y=conf.height - action_height,
                                border_fg=term.YELLOW,
                                
    )
    viewport = screen.make_box(conf.viewport_width, conf.viewport_height,
                                x=conf.width - conf.viewport_width,
                                border_fg=term.RED,
    )

@event.on('explore.draw')
def draw_explore():
    viewport.draw()
    level.room.draw(viewport)

    action_zone.draw()

    
@event.on('explore.start')
def start_explore():
    level.room = room.create_room('ns_test.ans')
    state.player.explore_reset()


@event.on('explore.tick')
def explore_tick():
    log.debug("in tick")
    return

@event.on('explore.prompt')
def explore_prompt():
    if level.input_mode == 'level':
        level_prompt()
    else:
        #bottom menu
        pass

def level_prompt():
    while True:
        event.fire('flip')

        key = term.getkey()
        if key == 'enter':
            return

        elif key == 'up':
            if level.room.try_move(y=-1):
                return

        elif key == 'down':
            if level.room.try_move(y=+1):
                return

        elif key == 'left':
            if level.room.try_move(x=-1):
                return

        elif key == 'right':
            if level.room.try_move(x=+1):
                return

    
    return

