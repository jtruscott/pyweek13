import screen, event, state, term

import logging
log = logging.getLogger('battle')
i = 0

@event.on('setup')
def setup_battle_ui():

    global action_bar, action_text, enemy_zone, message_zone
    conf = state.config
    action_height = conf.height - conf.viewport_height
    action_bar = screen.make_box(conf.width, action_height,
                                y=conf.height - action_height,
                                border_fg=term.YELLOW,
                                
    )
    enemy_zone = screen.make_box(conf.viewport_width, conf.viewport_height,
                                x=conf.width - conf.viewport_width,
                                border_fg=term.RED,
    )
    action_text = screen.RichText("oh my god, it's a <RED>mutant!</> (<GREEN>%i</>)", x=1, y=5, center_to=action_bar.width-2)
    action_bar.children.append(action_text)

@event.on('battle.draw')
def draw_battle():
    action_text.format(i)
    action_bar.draw()
    enemy_zone.draw()
    
@event.on('battle.start')
def start_battle():
    pass

@event.on('battle.prompt')
def battle_prompt():
    term.getkey()
    global i
    i += 1
