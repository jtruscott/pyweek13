import event, message, term, state, screen, room, layouts, player
import sound

import logging
log = logging.getLogger('explore')
class level:
    layout = None
    input_mode = 'level'

    been_cursed = False

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

def add_room_messages():
    messages = level.layout.curr_room.explore_messages
    statblock = player.statblock
    player.update_player_statblock(state.player)
    
    x = statblock.width + statblock.x + 1
    y = 1
    texts = [statblock]
    for message in messages:
        text = screen.RichText(message, x=x, y=y, wrap_to=action_zone.width-2)
        texts.append(text)
        y += text.height + 1
    action_zone.children = texts
    action_zone.dirty = True

@event.on('explore.start')
def start_explore():
    sound.play('appear')
    level.layout = layouts.start_layout()
    level.layout.setup()
    state.player.reset_hp()
    state.player.explore_reset()
    
    add_room_messages()

    message.add("""
<LIGHTGREY>This is the cursed isle of <WHITE>Melimnor</>,
spoke of in legend to be rife with hideous,
deformed, and unnatural creatures.</>

By some horrible luck, you find yourself on
it's shores. It is eerily quiet here.
""")

@event.on('explore.resume')
def resume_explore(defeated=False):
    if defeated:
        level.layout.curr_room.buf.dirty = True
    else:
        state.after_battle_tile.clear()
        level.layout.curr_room.move_player(*state.after_battle_pos)
    state.player.reset_hp()
    player.update_player_statblock(state.player)
    action_zone.dirty = True
    for child in action_zone.children:
        child.dirty = True

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
        if key in ('up', 'down', 'left', 'right') and not level.been_cursed:
            message.newline()
            message.add("The curse of Melimnor takes hold upon you!")
            state.player.add_limb()
            message.newline()
            level.been_cursed = True
        
        if key == 'enter':
            return
        
        elif key == 'f3' and False:
            #TAKE ME OUT BEFORE RELEASE
            state.player.mutate()
        elif key == 'f4' and False:
            #TAKE ME OUT BEFORE RELEASE
            state.player.add_limb()

        elif key == 'up':
            ret = level.layout.curr_room.try_move(y=-1)

        elif key == 'down':
            ret = level.layout.curr_room.try_move(y=+1)

        elif key == 'left':
            ret = level.layout.curr_room.try_move(x=-1)

        elif key == 'right':
            ret = level.layout.curr_room.try_move(x=+1)
        
        log.debug('ret: %r', ret)
        if not ret:
            continue
        elif ret is True:
            return
        else:
            action, args = ret
            log.debug("action: %r, args: %r", action, args)
            if action == 'changeroom':
                level.layout.change_room(*args)
                add_room_messages()
                draw_explore()
            elif action == 'changelevel':
                log.debug("changing level")
                level.layout = layouts.random_layout()
                state.found_key = False
                add_room_messages()
                draw_explore()
                message.add("<LIGHTRED>The stairs vanish behind you!")
    
    return

