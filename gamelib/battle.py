import screen, event, state, term, player, message, sound
import collections, random

import logging
log = logging.getLogger('battle')

enemy = None
selected_attack_index = None


@event.on('setup')
def setup_battle_ui():

    global action_zone, enemy_zone
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

@event.on('battle.draw')
def draw_battle():
    draw_player_attacks()

    action_zone.draw()
    enemy_zone.draw()

    
@event.on('battle.start')
def start_battle():
    global enemy, selected_attack_index
    enemy = player.Enemy()
    describe_enemy()

    state.player.battle_reset()
    enemy.battle_reset()

    list_player_attacks()
    selected_attack_index = 0


def describe_enemy():
    enemy_zone.children = [
        screen.RichText("Before you is a %s with %i hp!" % (enemy.name, enemy.hp), x=1, y=2, wrap_to=enemy_zone.width-2),
    ]
    y = 4
    def make_part_buffer(slot, part):
        return screen.RichText(
            "%s:\n    %s" % (slot.replace("_", " ").title(), (part.description % part.__dict__).replace("\n","\n    ")),
            x=1,y=y, wrap_to=enemy_zone.width-2
        )

    for slot in enemy.slots:
        if enemy.parts[slot]:
            part = enemy.parts[slot]
            text_block = make_part_buffer(slot, part)
            enemy_zone.children.append(text_block)
            y += text_block.height
    for slot in enemy.limbs:
        for part in enemy.parts[slot]:
            text_block = make_part_buffer(slot, part)
            enemy_zone.children.append(text_block)
            y += text_block.height
    enemy_zone.dirty = True

@event.on('battle.tick')
def battle_tick():
    log.debug("in tick, delays are %r and %r", state.player.cur_tick_delay, enemy.cur_tick_delay)
    while state.player.cur_tick_delay and enemy.cur_tick_delay:
        log.debug("spending tick")
        state.player.battle_tick()
        enemy.battle_tick()
    
    if not state.player.cur_tick_delay:
        #go to the prompt
        return
    if not enemy.cur_tick_delay:
        #enemy AI time
        attacks = enemy.do_action()
        if attacks:
            resolve_attack(attacks, enemy, state.player)
    return

@event.on('battle.prompt')
def battle_prompt():
    global selected_attack_index

    def selection_wrap(idx):
        global selected_attack_index
        idx = selected_attack_index + idx
        selected_attack_index = max(0, min(len(attack_names)-1, idx))
        log.debug('selected_attack_index: %r', selected_attack_index)
        sound.play('select')
        return

    #check for reasons to skip this turn
    if state.player.cur_tick_delay:
        #missing a turn
        return
    can_attack = False
    minimum_wait = 1
    for attack_tuple in player_attacks.values():
        if not attack_tuple.attacks[0].cur_cooldown:
            can_attack = True
            break
        minimum_wait = min(minimum_wait, attack_tuple.attacks[0].cur_cooldown)
    if not can_attack:
        message.add("<DARKGREY>No attacks available")
        message.add("<DARKGREY>%s delays for %i" % (state.player.name, minimum_wait))
        state.player.cur_tick_delay = minimum_wait
        return

    while True:
        sel_x, sel_y = draw_player_attacks()
        draw_attack_pointer(sel_x, sel_y)
        event.fire('flip')

        key = term.getkey()
        if key == 'enter':
            current = player_attacks[attack_names[selected_attack_index]]
            if current.attacks[0].cur_cooldown:
                message.error("That attack is on cooldown.", flip=True)
                continue

            else:
                #selection confirmed
                resolve_attack(current.attacks, state.player, enemy)
                return

        elif key == 'up':
            selection_wrap(-1)

        elif key == 'down':
            selection_wrap(+1)

        elif key == 'left':
            selection_wrap(-2)
        
        elif key == 'right':
            selection_wrap(+2)

    
    return

def list_player_attacks():
    global player_attacks, attack_names

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
        cooldown_buffer = create_cooldown_buffer(attacks)

        player_attacks[attack_name] = attack_tuple(attacks, unsel_buffer, sel_buffer, cooldown_buffer)
    attack_names = attack_types.keys()

def draw_player_attacks():
    x_base = x = 1
    x_skip = 21
    
    y_base = y = 1
    y_skip = 4
    y_max = 8

    sel_x = sel_y = 0
    attacks = []
    for attack_name in attack_names:
        attack_tuple = player_attacks[attack_name]
        
        if attack_tuple.attacks[0].cur_cooldown:
            buf = attack_tuple.cooldown_buffer
            cooldown_text = '<DARKGREY>%s' % ((
                    "(available in %i)" % (attack_tuple.attacks[0].cur_cooldown)
                    ).center(20))
            buf.children[1].set(cooldown_text)

        elif attack_name == attack_names[selected_attack_index]:
            log.debug('sel: %r [%i]', attack_name, selected_attack_index)
            buf = attack_tuple.sel_buffer

        else:
            buf = attack_tuple.unsel_buffer
        
        buf.x = x
        buf.y = y
        buf.dirty = True
        attacks.append(buf)

        if attack_name == attack_names[selected_attack_index]:
            sel_x = buf.x + action_zone.x
            sel_y = buf.y + action_zone.y

        y += y_skip
        if y >= y_max:
            y = y_base
            x += x_skip

    action_zone.children = attacks
    action_zone.dirty = True
    action_zone.draw()
    return sel_x, sel_y

def draw_attack_pointer(sel_x, sel_y):
    screen.left_pointer.x = sel_x
    screen.right_pointer.x = sel_x+20

    screen.left_pointer.y = sel_y
    screen.right_pointer.y = sel_y

    screen.left_pointer.dirty = True
    screen.right_pointer.dirty = True

    screen.left_pointer.draw()
    screen.right_pointer.draw()

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

    accuracy = sum([attack.calc_accuracy(owner) for attack in attacks]) / len(attacks)
    min_damage = sum([attack.calc_min_damage(owner) for attack in attacks])
    max_damage = sum([attack.calc_max_damage(owner) for attack in attacks])
    line2_len = len("Atk +%-2i Dmg %2i-%-2i" % (accuracy, min_damage, max_damage))
    line2 = "<DARKGREY>Atk <%s>+%-2i</> Dmg <%s>%2i-%-2i</>" % (name_color, accuracy, name_color, min_damage, max_damage)
    line2 = pad_alternate(line2, line2_len)

    speed = attacks[0].speed + (len(attacks) - 1) 
    cooldown = attacks[0].cooldown + (len(attacks) - 1)
    line3_len = len("Time %-2i Delay %2i " % (speed, cooldown))
    line3 = "<DARKGREY>Time <%s>%-2i</> Delay <%s>%2i</> " % (name_color, speed, name_color, cooldown)
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

def create_cooldown_buffer(attacks):
    max_width = 20
    line1 = '<DARKGREY>%s' % attacks[0].name.center(max_width)
    line2 = '' #dynamically set
    line3 = ''.center(max_width)
    
    container = screen.Buffer(width=max_width, height=3,
                    data=[[(term.WHITE, term.BLACK, ' ')]*20]*3,
                    children = [
                        screen.RichText(line1, y=0),
                        screen.RichText(line2, y=1),
                        screen.RichText(line3, y=2),
                    ]
    )
    return container

def describe_attack(attacks, owner, target):
    log.debug("Describing o=%r t=%r", owner, target)
    format_dict = dict(owner=owner.name, target=target.name)
    format_dict.update(attacks[0].__dict__)
    message.add("<WHITE>%s" % (attacks[0].attacktext % format_dict))

def resolve_attack(attacks, owner, target):
    def d20():
        return random.randint(1,20)
    combo = False
    speed_mod = 0
    duration_mod = 0
    accuracy_penalty = 0
    if len(attacks) > 1:
        combo = True
        speed_mod = (len(attacks) - 1)*2
        duration_mod = (len(attacks) - 1)*2
    describe_attack(attacks, owner, target)

    for attack in attacks:
        #to hit
        accuracy_roll = d20()
        accuracy_mod = attack.calc_accuracy(owner) - accuracy_penalty
        hit = (accuracy_roll + accuracy_mod >= target.evasion)
        accuracy_text = " <DARKGREY>(<GREEN>%i</><BROWN>%+i</> vs <LIGHTGREY>%i</>)" % (
                                    accuracy_roll, accuracy_mod, target.evasion)
        #damage
        if hit:
            message.add(" <LIGHTGREEN>Hit!  %s" % accuracy_text)
            damage_roll = d20()
            damage_mod = attack.calc_damage(owner)
            damage = max(0, damage_roll + damage_mod - target.armor)
            armor_penalty_text = target.armor and ("<RED>%+i</>" % target.armor) or ""
            message.add(" <LIGHTGREY>%s<DARKGREY> takes <LIGHTRED>%i</> damage! (<GREEN>%i</><BROWN>%+i</>%s)" % (
                                    target.name, damage, damage_roll, damage_mod, armor_penalty_text))
            target.take_damage(damage)
            if attack.sound:
                sound.play(attack.sound, channel='attack', wait=True)
                
            if target.cur_hp <= 0:
                message.add("<YELLOW>%s was defeated!" % target.name)
                if target == state.player:
                    event.fire('player.defeated')
                else:
                    event.fire('enemy.defeated')
                break

        else:
            message.add(" <LIGHTRED>Miss! %s" % accuracy_text)

        message.newline()
        #attack bookkeeping
        attack.cur_cooldown = attack.cooldown + duration_mod
        accuracy_penalty += 2
    
    #owner bookkeeping
    owner.cur_tick_cooldown = attacks[0].speed + speed_mod
    message.newline()

@event.on('enemy.defeated')
def enemy_defeated():
    state.mode = 'explore'
    event.fire('explore.resume')
    raise state.StateChanged()

@event.on('player.defeated')
def player_defeated():
    #THERE IS NO ESCAPE
    message.error("You died!", flip=True)
    state.mode = 'explore'
    event.fire('explore.start')
