import screen, event, state, term, player, message

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
    
    test = create_attack_buffer([state.player.parts['left_arm'][0]], state.player, False)
    test.x = 1
    test.y = 1
    action_bar.children.append(test)

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

def create_attack_buffer(attacks, owner, selected=False):
    """
        'attacks' is an array of the Attack objects in this combo.
                all attacks should be of identical type.
    """
    max_width=20

    if selected:
        name_color = 'WHITE'
    else:
        name_color = 'LIGHTGREY'
    def pad_alternate(line, base_width):
        """
            like .center() but using an alternate width
            because of our rich text shenanigans
        """
        line = "%s%s%s" % (' ' * ((max_width-base_width)/2), line, ' ' * ((max_width-base_width)/2))
        return line
    
    if len(attacks):
        line1 = "%ix %s" % (count, attacks[0].name)
    else:
        line1 = "%s" % attacks[0].name
    line1 = '<%s>%s</>' % (name_color, line1.center(max_width))

    accuracy = sum([attack.calc_min_damage(owner) for attack in attacks]) / len(attacks)
    min_damage = sum([attack.calc_min_damage(owner) for attack in attacks])
    max_damage = sum([attack.calc_max_damage(owner) for attack in attacks])
    line2_len = len("Atk +%i Dmg %i-%i" % (accuracy, min_damage, max_damage))
    line2 = "<Atk <%s>+%i</> Dmg <%s>%i-%i</>" % (name_color, accuracy, name_color, min_damage, max_damage)
    line2 = pad_alternate(line2, line2_len)

    speed = attacks[0].speed + (len(attacks) - 1) 
    cooldown = attacks[0].cooldown + (len(attacks) - 1)
    line3_len = len("Time %i Delay %i" % (speed, cooldown))
    line3 = "Time <%s>%i</> Delay <%s>%i</>" % (name_color, speed, name_color, cooldown)
    line3 = pad_alternate(line3, line3_len)

    container = screen.Buffer(width=max_width, height=3,
                    data=[[(term.WHITE, term.BLACK, ' ')]*20]*3],
                    children = [
                        screen.RichText(line1, y=0),
                        screen.RichText(line2, y=1),
                        screen.RichText(line3, y=2),
                    ]
    )
    return container
