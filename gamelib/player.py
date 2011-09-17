import random
import event
import parts
import message
import logging
log = logging.getLogger('player')

class Humanoid:
    name = "Humanoid"
    cur_hp = 0
    base_hp = 20
    bonus_hp = 30
    quest_accuracy_bonus = 0

    slots = [
        'head',
        'body',
        'legs',

        'tail',
    ]
    limbs = [
        'left_arm',
        'right_arm'
    ]
    def __init__(self):
        self.parts = {}
        for slot in self.slots:
            self.parts[slot] = None
        for limb in self.limbs:
            self.parts[limb] = []

    def calc_stats(self):
        self.hp = self.base_hp + self.bonus_hp
        self.armor = 0
        self.evasion = 10
        self.damage_bonus = 0
        self.accuracy_bonus = self.quest_accuracy_bonus
        self.proc_chance_bonus = 0.0

        for slot in self.slots:
            part = self.parts[slot]
            if part is None:
                continue
            part.add_bonus(self)
        
        log.debug("Stats: hp=%r, armor=%s, evasion=%r, +dmg=%r, +acc=%r, +proc=%r",
            self.hp, self.armor, self.evasion,
            self.damage_bonus, self.accuracy_bonus, self.proc_chance_bonus
        )

    def reset_status(self):
        self.status = None

    def all_parts(self):
        """
            Generator to iterative over all parts in a Humanoid
        """
        for slot in self.slots:
            if not self.parts[slot]:
                continue
            yield self.parts[slot]
        for limb_slot in self.limbs:
            for limb in self.parts[limb_slot]:
                yield limb

    def explore_reset(self):
        return
    
    def battle_reset(self):
        self.cur_hp = self.hp
        self.cur_tick_delay = 0
        for part in self.all_parts():
            part.battle_reset()
    
    def reset_hp(self):
        self.cur_hp = self.hp
    
    def battle_tick(self):
        if self.cur_tick_delay:
            self.cur_tick_delay -= 1
        for part in self.all_parts():
            log.debug("ticking on %r", self.name)
            part.battle_tick()

    def take_damage(self, damage):
        log.debug("%s taking %r damage", self.name, damage)
        self.cur_hp = max(0, self.cur_hp - damage)

    def random_part(self, slot):
        if slot in self.limbs:
            slot = 'limbs'
        return parts.get_part(random.choice(parts.parts[slot]))

    def add_part(self, slot, part):
        log.debug("adding a %r part: %r", slot, part.name)
        if slot in self.limbs:
            self.parts[slot].append(part)
        else:
            self.parts[slot] = part

class Player(Humanoid):
    name = "Player"
    found_artifacts = 0
    losses = 0
    def __init__(self, *args, **kwargs):
        Humanoid.__init__(self, *args, **kwargs)
        self.reset_body()
        self.calc_stats()

        self.reset_status()
        update_player_statblock(self)

    def reset_body(self):
        self.parts['head'] = parts.get_part(parts.by_name['Human Head'])
        self.parts['body'] = parts.get_part(parts.by_name['Human Torso'])
        self.parts['legs'] = parts.get_part(parts.by_name['Human Legs'])
        #self.parts['back'] = None
        self.parts['tail'] = None

        self.parts['left_arm'] = [parts.get_part(parts.by_name['Human Arm'])]
        self.parts['right_arm'] = [parts.get_part(parts.by_name['Human Arm'])]

    def ask_user(self):
        while True:
            key = term.getkey()
            if key not in ('y', 'Y', 'n', 'N'):
                message.error("Please choose 'Y' or 'N'", flip=True)
                continue
            if key in ('y', 'Y'):
                return True
            if key in ('n', 'N'):
                return False
                    
    def mutate(self):
        #find something new
        log.debug("Mutating!")
        message.add("<MAGENTA>The curse of Melimnor twists your body!", flip=True)
        vetos = 0
        last_vetoed = None
        while True:
            slot = random.choice(self.slots + self.limbs)
            part = self.random_part(slot)
            log.debug("Testing a %r part %r", slot, part.name)
            if 'Human' in part.name:
                #can never go back, buddy
                continue

            if part.name == last_vetoed:
                #don't reroll the same part that was just vetoed
                #(cycles are totally okay)
                continue

            if slot in self.limbs:
                old_part = random.choice(self.parts[slot])
                if part.name == old_part.name:
                    #that wouldn't be much of a mutation
                    continue
            else:
                old_part = self.parts[slot]
                if old_part and part.name == old_part.name:
                    #that wouldn't be much of a mutation
                    continue
            
            #ask if they want it - if they can
            if vetos >= self.found_artifacts:
                #too bad!
                break
            message.add("<GREEN>Your <LIGHTGREEN>Melimnarian Artifact</> glows with power!")
            message.add("<WHITE>Do you accept a <LIGHTMAGENTA>%s</>? (Y/N)" % part.name, flip=True)
            if self.ask_user():
                message.add("<WHITE>You have accepted the <LIGHTMAGENTA>%s</>." % part.name, flip=True)
                break
            else:
                message.add("<WHITE>You force the magical curse to try again.", flip=True)
                vetos += 1
                last_vetoed = part.name
                
        #set it
        log.debug("Chose a %r part %r", slot, part.name)
        if slot in self.limbs:
            idx = self.parts[slot].index(old_part)
            self.parts[slot][idx] = part
        else:
            self.parts[slot] = part
        
        #tell them about it            
        slot_name = slot.replace("_", " ").title()
        if old_part:
            message.add("<LIGHTMAGENTA>Your %s mutates into a %s!" % (slot_name, part.name), flip=True)
        else:
            message.add("<LIGHTMAGENTA>A %s sprouts from your %s!" % (part.name, slot_name), flip=True)
        
        message.newline(flip=True)
        self.calc_stats()

    def add_limb(self):
        log.debug("Adding limb!")
        message.add("<MAGENTA>The magic of Melimnor grants you a new limb!", flip=True)
        slot = random.choice(self.limbs)
        part = self.random_part(slot)
        self.add_part(slot, part)

        slot_name = slot.replace("_", " ").title()
        message.add("<LIGHTMAGENTA>You now have a new %s on your %s!" % (part.name, slot_name), flip=True)

        self.calc_stats()

        

class Enemy(Humanoid):
    name = "Mutant"
    def __init__(self, monster_level=None, *args, **kwargs):
        Humanoid.__init__(self, *args, **kwargs)
        self.generate_body(monster_level)
        self.calc_stats()

        self.reset_status()

    def generate_body(self, monster_level):
        log.debug("Generating class-%i enemy", monster_level)
        #start off human-like
        base_parts = {
            'head': parts.get_part(parts.by_name['Human Head']),
            'body': parts.get_part(parts.by_name['Human Torso']),
            'legs': parts.get_part(parts.by_name['Human Legs']),
            'left_arm': parts.get_part(parts.by_name['Human Arm']),
            'right_arm': parts.get_part(parts.by_name['Human Arm']),
            'tail': None
        }
        #determine how mutated to be
        mutation_count = 0
        extra_limbs = 0

        if monster_level == 0:
            mutation_count = 1
            max_extra_limbs = 0
            monster_level = 1
        else:
            mutation_count = monster_level + 2
            extra_limbs = max(0, random.randint(monster_level - 2, monster_level + 1))


        #do some mutatin'
        for i in range(mutation_count):
            for attempt in range(20):
                slot = random.choice(base_parts.keys())
                part = self.random_part(slot)
                if part.power > monster_level or part.power < monster_level-1:
                    if attempt >= 19:
                        log.debug("forced to accept a %r, power = %r and level = %r",part.name, part.power, monster_level)
                        break
                    log.debug("skipping a %r, power = %r and level = %r",part.name, part.power, monster_level)
                    continue
                break

            log.debug("mutating the %r into a %r", slot, part.name)
            self.add_part(slot, part)

            #take it out of the base_parts set so we don't re-mutate the same component
            del base_parts[slot]
        
        #put the regular, unmutated bits in
        for slot, part in base_parts.items():
            if not part:
                continue
            self.add_part(slot, part)

        #do some farm-fresh limb growin'
        log.debug("adding %r extra limbs", extra_limbs)
        for i in range(extra_limbs):
            for attempt in range(20):
                new_limb = self.random_part('limbs')
                if new_limb.power > monster_level or new_limb.power < monster_level-1:
                    if attempt >= 19:
                        log.debug("forced to accept a %r limb, power = %r and level = %r", new_limb.name, new_limb.power, monster_level)
                        break
                    log.debug("skipping a %r limb, power = %r and level = %r", new_limb.name, new_limb.power, monster_level)
                    continue
                break
            slot = random.choice(['left_arm', 'right_arm'])
            log.debug("adding a %r to the %r", new_limb.name, slot)
            self.parts[slot].append(new_limb)
        log.debug("generation complete")

    def do_action(self):
        log.debug("doing action")
        all_attacks = [part.attack for part in self.all_parts() if part.attack]

        min_delay = min([attack.cur_cooldown for attack in all_attacks])
        if min_delay:
            log.debug("cooldowns: %r", [(attack.name, attack.cur_cooldown) for attack in all_attacks])
            message.add("<DARKGREY>%s delays for %i" % (self.name, min_delay))
            self.cur_tick_delay = min_delay
            return
        
        available_attacks = {}
        for attack in all_attacks:
            if attack.cur_cooldown:
                continue
            available_attacks.setdefault(attack.name, [])
            available_attacks[attack.name].append(attack)    
        
        #build a list of (duration, combo) so we can use max() to find the slowest one
        dur, chosen_attack = max([((attacks[0].cooldown + ((len(attacks) - 1)*2)), attacks) for attacks in available_attacks.values()])
        return chosen_attack

class Boss(Enemy):
    name = "Boss"

class OwlbearBoss(Boss):
    name = "Owlbear"
    def generate_body(self, *args, **kwargs):
        self.parts['head'] = parts.get_part(parts.by_name['Owl Head'])
        self.parts['body'] = parts.get_part(parts.by_name['Feathered Torso'])
        self.parts['legs'] = parts.get_part(parts.by_name['Bear Legs'])

        self.parts['left_arm'] = [
                parts.get_part(parts.by_name['Feathered Arm'])
        ]
        self.parts['right_arm'] = [
                parts.get_part(parts.by_name['Feathered Arm'])
        ]


import state, term
@event.on('setup')
def setup_player_statblock():
    global statblock
    import screen
        
    conf = state.config
    statblock = screen.make_box(
        width=(conf.width - conf.viewport_width) / 2,
        height=conf.height - conf.viewport_height,
        x=0,
        y=0,
        border_fg=term.BLUE,
        draw_top=False,
    )
    statblock.children = [
        screen.RichText(x=1, y=1, message="<WHITE>%s" % ("Player".center(statblock.width-2))),
        screen.RichText(x=1, y=2, message="HP: <%s>%i<LIGHTGREY> / <WHITE>%i</>"),
        screen.RichText(x=1, y=3, message="Armor:   <WHITE>%i</>"),
        screen.RichText(x=1, y=4, message="Evasion: <WHITE>%i</>"),
        screen.RichText(x=1, y=5, message="+Atk:    <WHITE>%i</>"),
        screen.RichText(x=1, y=6, message="+Dmg:    <WHITE>%i</>"),
        screen.RichText(x=1, y=8, message="Defeats: <WHITE>%i</>"),
    ]

def update_player_statblock(player):
    global statblock

    name, hp, armor, evasion, atk, dmg, defeats = statblock.children
    
    hp_color = 'LIGHTRED'
    hp_pct = float(player.cur_hp) / player.hp

    if hp_pct > 0.33:
        hp_color = 'YELLOW'
    if hp_pct > 0.66:
        hp_color = 'LIGHTGREEN'

    hp.format((hp_color, player.cur_hp, player.hp))
    armor.format((player.armor))
    evasion.format((player.evasion))
    atk.format((player.accuracy_bonus))
    dmg.format((player.damage_bonus))
    defeats.format((player.losses))
    statblock.dirty = True
