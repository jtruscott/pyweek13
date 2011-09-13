import random

from attacks import *

import logging
log = logging.getLogger('parts')

#dictionary of name:part for lookups
by_name = {}

words = {
    "human":["mundane", "boring", "uninteresting", "ordinary"],
    "bug": ["insectoid", "buglike"],
    "avian": ["avian"],
    "animal": ["mammalian"],
    "fish": ["squamous", "ichthyoidal", "fishlike"],
    "ceph": ["cephalopodic"],
    "robo": ["metallic", "robotic"],
    "bio": ["organic",],
    "stone": ["granite", "basalt", "marble", ],
    "fire": ["flaming", "firey"],
    "storm": ["stormy", "crackling", "thunderous"],
}
def random_adjective(theme):
    if theme not in words:
        log.debug("Theme not in words: %s", theme)
        return theme
    return random.choice(words[theme])
    
    

class Part:
    def __init__(self, name, description, theme,
                    hp=0, armor=0, evasion=0,
                    damage_bonus=0, accuracy_bonus=0, proc_chance_bonus=0,
                    attack=None
                ):
        #themes are as follows: human, bug, avian, animal, fish, ceph (for cepholopoidial), robo, bio, fire, storm, stone
        
        self.name = name
        self.adjective = random_adjective(theme)
        self.description = description
        self.hp = hp
        self.armor = armor
        self.evasion = evasion

        self.damage_bonus = damage_bonus 
        self.accuracy_bonus = accuracy_bonus
        self.proc_chance_bonus = proc_chance_bonus
        
        self.attack = attack

        #register ourselves
        by_name[name] = self
        

    def add_bonus(self, target):
        target.hp += self.hp
        target.armor += self.armor
        target.evasion += self.evasion

        target.damage_bonus += self.damage_bonus 
        target.accuracy_bonus += self.accuracy_bonus
        target.proc_chance_bonus += self.proc_chance_bonus
    
    def battle_reset(self):
        if self.attack:
            self.attack.battle_reset()


parts = {
    'head': [
        Part("Human Head", "A perfectly normal human head", "mundane", attack=BiteAttack()),
        Part("Spider Head", "An enormous, %(adjective)s spider's head, with compound eyes and sharp mandibles that drip venom", "bug",
             #attack=BiteAttack(status=poison)
             ),
        Part("Wolf's Head", "A long, canine snout, full of sharp teeth", "animal", attack=BiteAttack(damage=1))
    ],
    'body': [
        Part("Human Torso", "A perfectly normal human torso", "human"),
        Part("Strong Human Torso", "A muscular human torso", "human", hp=1),
        Part("Scaled Torso", "A torso covered in thick, durable scales", "fish", armor=1, hp=2),
    ],
    'legs': [
        Part("Human Legs", "A perfectly normal pair of human legs", "mundane", attack=LaserAttack()),
    ],
    'back': [],
    'tail': [],

    'limbs': [
        Part("Human Arm", "A perfectly normal human arm", "human", attack=PunchAttack()),
        Part("Strong Human Arm", "A very strong human arm", "human", attack=PunchAttack(damage=1)),
    ]
}

print random_adjective("fish")
