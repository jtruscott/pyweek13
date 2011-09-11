import parts

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
        self.hp = 10
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

        self.parts['left_arm'] = parts.by_name['Human Arm']
        self.parts['right_arm'] = parts.by_name['Human Arm']
