import screen, event, state, term, player, message
import collections

import logging
log = logging.getLogger('battle')
i = 0
enemy = None

@event.on('setup')
def setup_battle_ui():

    global action_zone, action_text, enemy_zone
    conf = state.config
    action_height = conf.height - conf.viewport_height
    action_zone = screen.make_box(conf.width, action_height,
                                y=conf.height - action_height,
                                border_fg=term.YELLOW,
                                
    )
    enemy_zone = screen.make_box(conf.viewport_width, conf.viewport_height,
                                x=conf.width - conf.viewport_width,
                                border_fg=term.RED,
    )
    action_text = screen.RichText("oh my god, it's a <RED>mutant!</> (<GREEN>%i</>)", x=1, y=5, center_to=action_zone.width-2)
    action_zone.children.append(action_text)

@event.on('battle.draw')
def draw_battle():
    draw_player_attacks()

    action_text.format(i)
    action_zone.draw()
    enemy_zone.draw()

    
@event.on('battle.start')
def start_battle():
    global enemy, selected_attack
    enemy = player.Enemy()
    describe_enemy()

    state.player.battle_reset()
    enemy.battle_reset()

    list_player_attacks()
    selected_attack = player_attacks.keys()[0]


def describe_enemy():
    enemy_zone.children = [
        screen.RichText("Before you is a %s with %i hp!" % (enemy.name, enemy.hp), x=1, y=2, center_to=enemy_zone.width-2, wrap_to=enemy_zone.width-2),
    ]
    y = 4
    for slot in enemy.slots:
        if enemy.parts[slot]:
            part = enemy.parts[slot]
            text_block = screen.RichText(
                "it's %s: %s" % (slot, (part.description % part.__dict__)),
                x=1,y=y, center_to=enemy_zone.width-2, wrap_to=enemy_zone.width-2
            )
            enemy_zone.children.append(text_block)
            y += text_block.height
    enemy_zone.dirty = True

@event.on('battle.prompt')
def battle_prompt():
    term.getkey()
    global i
    i += 1

def list_player_attacks():
    global player_attacks

    attack_types = {}
        
    for part in state.player.all_parts():
        if not part.attack:
            continue
        attack = part.attack
        attack_types.setdefault(attack.name, [])
        attack_types[attack.name].append(attack)
    
    log.debug("attack_types: %r", attack_types)
    
    player_attacks = {}
    
    #create a named tuple so we have field names
    attack_tuple = collections.namedtuple('AttackTuple', ('attacks', 'unsel_buffer', 'sel_buffer', 'cooldown_buffer'))

    for attack_name, attacks in attack_types.items():
        unsel_buffer = create_attack_buffer(attacks, state.player)
        sel_buffer = create_attack_buffer(attacks, state.player, selected=True)
        cooldown_buffer = None

        player_attacks[attack_name] = attack_tuple(attacks, unsel_buffer, sel_buffer, cooldown_buffer)

def draw_player_attacks():
    x_base = x = 1
    x_skip = 21
    
    y_base = y = 1
    y_skip = 4
    y_max = 8

    attacks = []
    for attack_name, attack_tuple in player_attacks.items():
        if attack_name == selected_attack:
            buf = attack_tuple.sel_buffer
        else:
            buf = attack_tuple.unsel_buffer
        
        buf.x = x
        buf.y = y
        attacks.append(buf)

        y += y_skip
        if y >= y_max:
            y = y_base
            x += x_skip

    action_zone.children = attacks


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
    
    if len(attacks) > 1:
        line1 = "%ix %s" % (len(attacks), attacks[0].name)
    else:
        line1 = "%s" % attacks[0].name
    line1 = '<%s>%s</>' % (name_color, line1.center(max_width))

    accuracy = sum([attack.calc_min_damage(owner) for attack in attacks]) / len(attacks)
    min_damage = sum([attack.calc_min_damage(owner) for attack in attacks])
    max_damage = sum([attack.calc_max_damage(owner) for attack in attacks])
    line2_len = len("Atk +%i Dmg %i-%i" % (accuracy, min_damage, max_damage))
    line2 = "Atk <%s>+%i</> Dmg <%s>%i-%i</>" % (name_color, accuracy, name_color, min_damage, max_damage)
    line2 = pad_alternate(line2, line2_len)

    speed = attacks[0].speed + (len(attacks) - 1) 
    cooldown = attacks[0].cooldown + (len(attacks) - 1)
    line3_len = len("Time %i Delay %i" % (speed, cooldown))
    line3 = "Time <%s>%i</> Delay <%s>%i</>" % (name_color, speed, name_color, cooldown)
    line3 = pad_alternate(line3, line3_len)

    container = screen.Buffer(width=max_width, height=3,
                    data=[[(term.WHITE, term.BLACK, ' ')]*20]*3,
                    children = [
                        screen.RichText(line1, y=0),
                        screen.RichText(line2, y=1),
                        screen.RichText(line3, y=2),
                    ]
    )
    return container
