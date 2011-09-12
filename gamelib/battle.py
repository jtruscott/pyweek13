import screen, event, state, term, player

import logging
log = logging.getLogger('battle')
i = 0
enemy = None

@event.on('setup')
def setup_battle_ui():

    global action_bar, action_text, enemy_zone
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
    global enemy
    enemy = player.Enemy()
    describe_enemy()

def describe_enemy():
    enemy_zone.children = [
        screen.RichText("Before you is a %s with %i hp!" % (enemy.name, enemy.hp), x=1, y=2, center_to=enemy_zone.width-2),
    ]
    y = 4
    for slot in enemy.slots:
        if enemy.parts[slot]:
            part = enemy.parts[slot]
            enemy_zone.children.append(screen.RichText(
                "it's %s: %s" % (slot, part.description),
                x=1,y=y, center_to=enemy_zone.width-2
            ))
            y += 1
    enemy_zone.dirty = True

@event.on('battle.prompt')
def battle_prompt():
    term.getkey()
    global i
    i += 1
