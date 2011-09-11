import screen, event, state, term

import logging
log = logging.getLogger('battle')
i = 0

@event.on('setup')
def setup_battle_ui():

    global action_bar, action_text
    action_height = 10
    action_bar = screen.make_box(state.config.width, action_height,
                                y=state.config.height - action_height,
                                border_fg=term.YELLOW,
                                draw_bottom=False
    )
    action_text = screen.RichText("oh my god, it's a <RED>mutant!</> (<GREEN>%i</>)", x=1, y=5, center_to=action_bar.width-2)
    action_bar.children.append(action_text)

@event.on('battle.draw')
def draw_battle():
    if state.mode is not 'battle':
        return
    action_text.format(i)
    action_bar.draw()
    
@event.on('battle.start')
def start_battle():
    pass

@event.on('battle.prompt')
def battle_prompt():
    import time
    time.sleep(1)
    global i
    i += 1
