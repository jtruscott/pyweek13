import random
import parts
import message
import logging
log = logging.getLogger('player')

class Humanoid:
    name = "Humanoid"
    slots = [
        'head',
        'body',
        'legs',

        'back',
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
        self.hp = 20
        self.armor = 0
        self.evasion = 10
        self.damage_bonus = 0
        self.accuracy_bonus = 0
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

    def battle_reset(self):
        self.cur_hp = self.hp
        self.cur_tick_delay = 0
        for part in self.all_parts():
            part.battle_reset()
    
    def battle_tick(self):
        if self.cur_tick_delay:
            self.cur_tick_delay -= 1
        for part in self.all_parts():
            part.battle_tick()

    def take_damage(self, damage):
        log.debug("%s taking %r damage", self.name, damage)
        self.cur_hp = max(0, self.cur_hp - damage)

class Player(Humanoid):
    name = "Player"
    def __init__(self, *args, **kwargs):
        Humanoid.__init__(self, *args, **kwargs)
        self.reset_body()
        self.calc_stats()

        self.reset_status()

    def reset_body(self):
        self.parts['head'] = parts.by_name['Human Head']
        self.parts['body'] = parts.by_name['Human Torso']
        self.parts['legs'] = parts.by_name['Human Legs']
        self.parts['back'] = None
        self.parts['tail'] = None

        self.parts['left_arm'] = [parts.by_name['Human Arm']]
        self.parts['right_arm'] = [parts.by_name['Human Arm']]


class Enemy(Humanoid):
    name = "Mutant"
    def __init__(self, *args, **kwargs):
        Humanoid.__init__(self, *args, **kwargs)
        self.generate_body()
        self.calc_stats()

        self.reset_status()

    def generate_body(self):
        for slot in ['head', 'body', 'legs']:
            self.parts[slot] = self.random_part(slot)
        for limb in self.limbs:
            self.parts[limb] = [self.random_part('limbs')]

    def random_part(self, slot):
        return random.choice(parts.parts[slot])

    def do_action(self):
        log.debug("doing action")
        all_attacks = [part.attack for part in self.all_parts() if part.attack]

        min_delay = min([attack.cur_cooldown for attack in all_attacks])
        if min_delay:
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
