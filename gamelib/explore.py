import event, message, term, state, screen, room, layouts

import logging
log = logging.getLogger('explore')
class level:
    layout = None
    input_mode = 'level'

@event.on('setup')
def setup_explore_ui():

    global action_zone, viewport
    conf = state.config
    action_height = conf.height - conf.viewport_height
    action_zone = screen.make_box(conf.width, action_height,
                                y=conf.height - action_height,
                                border_fg=term.BLUE,
                                draw_top=False,
                                
    )
    viewport = screen.make_box(conf.viewport_width, conf.viewport_height,
                                x=conf.width - conf.viewport_width,
                                border_fg=term.BLUE,
                                boxtype=term.BoxSingle,
    )

@event.on('explore.draw')
def draw_explore():
    viewport.draw()
    level.layout.curr_room.draw(viewport)

    action_zone.draw()

    
@event.on('explore.start')
def start_explore():
    level.layout = layouts.start_layout
    level.layout.setup()

    state.player.explore_reset()

@event.on('explore.resume')
def resume_explore():
    state.after_battle_tile.clear()
    level.room.move_player(*state.after_battle_pos)

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

        ret = False
        key = term.getkey()
        if key == 'enter':
            return

        elif key == 'up':
            ret = level.layout.curr_room.try_move(y=-1)

        elif key == 'down':
            ret = level.layout.curr_room.try_move(y=+1)

        elif key == 'left':
            ret = level.layout.curr_room.try_move(x=-1)

        elif key == 'right':
            ret = level.layout.curr_room.try_move(x=+1)
        
        if not ret:
            continue
        elif ret is True:
            return
        else:
            action, args = ret
            if action == 'changeroom':
                level.layout.change_room(*args)
    
    return

