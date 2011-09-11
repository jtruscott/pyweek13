from attacks import *

#dictionary of name:part for lookups
by_name = {}

class Part:
    def __init__(self, name, description,
                    hp=0, armor=0, evasion=0,
                    damage_bonus=0, accuracy_bonus=0, proc_chance_bonus=0,
                    attack=None
                ):
        
        self.name = name
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

parts = {
    'head': [
        Part("Human Head", "A perfectly normal human head"),
    ],
    'body': [
        Part("Human Torso", "A perfectly normal human torso"),
    ],
    'legs': [
        Part("Human Legs", "A perfectly normal pair of human legs"),
    ],
    'back': [],
    'tail': [],

    'limbs': [
        Part("Human Arm", "A perfectly normal human arm", attack=PunchAttack()),
        Part("Bulky Human Arm", "A very strong human arm", attack=PunchAttack(bonus=1)),
    ]
}
