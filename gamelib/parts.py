import random

from attacks import *

import logging
log = logging.getLogger('parts')

#dictionary of name:part for lookups
by_name = {}

words = {
    "human":["mundane", "boring", "uninteresting", "ordinary", "human"],
    "bug": ["insectoid", "buglike", "arachnidan", "vespine", "wasplike", "myrmecine", "antlike", "chitinous", "exoskeletal"],
    "avian": ["avian", "birdly", "birdlike", "feathered", "vulturelike", "corvine", "sleek", ],
    "animal": ["mammalian", "beastly", "monstrous", "lupinefant", "ursine", "feline", "equine"],
    "fish": ["squamous", "ichthyoidal", "fishlike", "piscine", "scaled", "streamlined"],
    "ceph": ["cephalopodic", "noisome", "amorphous", "many-tentacled", "molluscular", "wiggly", "undulating", "antedeluvian"],
    "robo": ["metallic", "robotic", "cold", "unfeeling", "angular", "industrial", "ferrous", "unyielding", "statuesque"],
    "bio": ["organic", "rugose", "fleshy", "muscular", "grotesque", "aberrant", "monstrous", "unwholesome", "inside-out"],
    "stone": ["granite", "basalt", "marble", "diamond", "obsidian", "flint", "chert", "gneiss", "slate", "limestone"],
    "fire": ["flaming", "firey", "conflagrative", "infernal", "inflammable", "inflammatory"],
    "storm": ["storming", "crackling", "thunderous", "roiling", "whirling", "cacaphonous", "turbulent", "humid", "meterologically active"],
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
                    attack=None, dire=False
                ):
        #"dire" means that the part is scaled for use in the final everything-goes floor
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
        
        self.dire = dire

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
        Part("Human Head", "A perfectly %(adjective)s human head", "mundane",),
        Part("Beast Head", "A long, %(adjective)s snout, full of sharp teeth", "animal",
             attack=BiteAttack(damage=1,attacktext="%(owner)s flails at the %(target)s with a puny human fist!")),
        Part("Animalistic Head", "A stout, %(adjective)s face, with eyes full of killing instinct", "animal", damage_bonus=2),
        Part("Fanged Head", "An enormous, %(adjective)s head, with compound eyes and sharp mandibles that drip venom", "bug",
             attack=BiteAttack()),
        Part("Teleporter-Accident Head", "A grotesque, %(adjective)s head like a fly, with enormous sets of compound eyes and a proboscis", "bug", evasion=2, accuracy_bonus=1),
        Part("Beaked Head", "A furtive, %(adjective)s head, with a great, sharp beak", "avian", evasion=1,
             attack=BiteAttack(speed=-1, attacktext="%(owner)s tries to pluck out the eyes of %(target)s with a great beak!")),
        Part("Shark Head", "A fearsome, %(adjective)s head, with multiple rows of sharp, ripping teeth", "fish",
             attack=BiteAttack(numdice=2, dietype=5, speed=-1, attacktext="JAWS 7: %(owner)s VERSUS %(target)s IN MORTAL COMBAT!")),
        Part("Swordfish Head", "A long, %(adjective)s head, with an enormous, bony spike protrouding from the end", "fish",
             attack=StabAttack(numdice=2, dietype=4, speed=-1, attacktext="%(owner)s lunges with at %(target)s with the enormous spike coming out of its face!")),
    ],
        
    'body': [
        Part("Human Torso", "A perfectly %(adjective)s human torso", "human"),
        #Part("Strong Human Torso", "A muscular human torso", "human", hp=1),
        Part("Scaled Torso", "A %(adjective)s torso covered in thick, durable scales", "fish", armor=1, hp=2),
    ],
        
    'legs': [
        Part("Human Legs", "A perfectly %(adjective)s pair of human legs", "mundane", attack=EnergyAttack(attacktext="Oh no! %(owner)s has a laser gun in its knee!")),
    ],
        
    'tail': [
        
    ],

    'limbs': [
        Part("Human Arm", "A perfectly %(adjective)s human arm", "human", attack=PunchAttack()),
        #Part("Strong Human Arm", "A very strong human arm", "human", attack=PunchAttack(damage=1)),
        Part("Beast Limb", "A powerfuly muscled, %(adjective)s limb, ending in sharp claws", "animal",
             attack=ClawAttack(attacktext="%(owner)s rends %(target)s with a sharp claw!")),
        Part("Bird Limb", "A lean, %(adjective)s limb, ending in sharp claws", "bird",
             attack=ClawAttack(speed=-1,damage=-2,attacktext="%(owner)s scratches %(target)s with a deft claw!")),
    ]
}
