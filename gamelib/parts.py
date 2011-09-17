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
    "animal": ["mammalian", "beastly", "monstrous", "lupine", "ursine", "feline", "equine"],
    "fish": ["squamous", "ichthyoidal", "fishlike", "piscine", "scaled", "streamlined"],
    "ceph": ["cephalopodic", "noisome", "amorphous", "tentacled", "molluscular", "wiggly", "undulating", "antedeluvian"],
    "robo": ["metallic", "robotic", "cold", "unfeeling", "angular", "industrial", "ferrous", "unyielding", "statuesque"],
    "bio": ["organic", "rugose", "fleshy", "muscular", "grotesque", "aberrant", "monstrous", "unwholesome", "inside-out"],
    "stone": ["granite", "basalt", "marble", "diamond", "obsidian", "flint", "chert", "gneiss", "slate", "limestone"],
    "fire": ["flaming", "firey", "conflagrative", "infernal", "inflammable", "inflammatory"],
    "storm": ["storming", "crackling", "thunderous", "roiling", "whirling", "cacaphonous", "turbulent", "humid",],
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

    def battle_tick(self):
        if self.attack:
            self.attack.battle_tick()

'''
Text descriptions should be no wider than 68 characters in width before \n.
Because "%(adjective)s" is as long as most of the adjective words, character counts can be done including those as-is.
Exceptions are for types human, ceph, and fire, which have character widths of 66, 67, and 66 again, respectively.
'''

parts = {
    'head': [
        Part("Human Head", "A perfectly %(adjective)s human head", "human",),
        Part("Beast Head", "A long, %(adjective)s snout, full of sharp teeth", "animal",
             attack=BiteAttack(damage=1,attacktext="%(owner)s flails at the %(target)s with a puny human fist!")),
        Part("Animalistic Head", "A stout, %(adjective)s face, with eyes full of killing instinct", "animal", damage_bonus=2),
        Part("Fanged Head", "An enormous, %(adjective)s head, with compound eyes and sharp\nmandibles that drip venom", "bug",
             attack=BiteAttack()),
        Part("Teleporter-Accident Head", "A grotesque, %(adjective)s head like a fly, with enormous sets of\ncompound eyes and a proboscis", "bug", evasion=2, accuracy_bonus=1),
        Part("Beaked Head", "A furtive, %(adjective)s head, with a great, sharp beak", "avian", evasion=1,
             attack=BiteAttack(speed=-1, attacktext="%(owner)s tries to pluck out the eyes of %(target)s with a great beak!")),
        Part("Shark Head", "A fearsome, %(adjective)s head, with multiple rows of sharp, ripping\nteeth", "fish",
             attack=BiteAttack(numdice=2, dietype=5, speed=-1, attacktext="JAWS 7: %(owner)s VERSUS %(target)s IN MORTAL COMBAT!")),
        Part("Swordfish Head", "A long, %(adjective)s head, with an enormous, bony spike protrouding\nfrom the end", "fish",
             attack=StabAttack(numdice=2, dietype=4, speed=-1, attacktext="%(owner)s lunges with at %(target)s with the enormous spike coming out of its face!")),
    ],
        
    'body': [
        Part("Human Torso", "A perfectly %(adjective)s human torso", "human", hp=10, evasion=-8),
        #Part("Strong Human Torso", "A muscular human torso", "human", hp=1),
        Part("Beastly Torso", "A great, furry, %(adjective)s body, rippling with muscle", "animal", hp=8, damage_bonus=2),
        Part("Avian Body", "An agile, %(adjective)s body", "avian", accuracy_bonus=2, evasion=2),
        Part("Scaled Torso", "A %(adjective)s torso covered in thick, durable scales", "fish", armor=3, hp=5),
        
    ],
        
    'legs': [
        Part("Human Legs", "A perfectly %(adjective)s pair of human legs", "human"),
        Part("Beastly Biped Legs", "A pair of great, furry, %(adjective)s legs.", "animal", hp=5, armor=1),
        Part("Mutantaur Legs", "A matched set of four hoofed %(adjective)s legs.", "animal", armor=2,
             attack=TrampleAttack(attacktext="%(owner)s tries to trample %(target)s) in a flurry of hooves!")),
        Part("Chicken Legs", "You ever notice that bird legs are actually kinda freaky?\nEspecially when they're human-sized.", "avian",
             evasion=1, armor=1, hp=2, attack=ClawAttack(attacktext="%(owner)s tries to scratch %(target)s with great oversided chicken legs!", damage=-2)),
        Part("Arachnid Legs", "Two legs are better than one; eight legs are SIGNIFICANTLY better\nthan two.", "bug"),
        Part("Octopoid Legs", "What's better than eight legs? Eight TENTACLES!", "ceph", hp=10,
             attack=BeatAttack())
    ],
        
    'tail': [
        Part("Basic Thagomizer", "An articulated tail with a wicked array of pointy bits and bony\ngrowths at the end.", "animal", armor=1, hp=2,
             attack=BeatAttack(attacktext="%(owner)s thagomizes %(target)s mightily!")),
        Part("Prehensile Tail", "A flexible, $(adjective)s tail that helps provide balance.", "animal", evasion=2),
        Part("Scorpion Stinger", "An armored tail with a great, wicked stinger.", "bug", armor=1,
             attack=StabAttack(dietype=8,attacktext="%(owner)s stabs at %(target)s with a great scorpion tail!")),
    ],

    'limbs': [
        Part("Human Arm", "A perfectly %(adjective)s human arm", "human", attack=PunchAttack()),
        #Part("Strong Human Arm", "A very strong human arm", "human", attack=PunchAttack(damage=1)),
        Part("Beast Limb", "A powerfuly muscled, %(adjective)s limb, ending in sharp claws", "animal",
             attack=ClawAttack(attacktext="%(owner)s rends %(target)s with a sharp claw!")),
        Part("Bird Limb", "A lean, %(adjective)s limb, ending in sharp claws", "avian",
             attack=ClawAttack(speed=-1,damage=-2,attacktext="%(owner)s scratches %(target)s with a deft claw!")),
        Part("Chitinous Claw", "A dark-colored, %(adjective)s pinching claw", "bug", armor=1,
             attack=ClawAttack(damage=2,attacktext="%(owner)s tries to grab tight with a great scorpionlike claw!")),
        Part("Crab Claw", "An oversized orange crustacean claw.", "fish", armor=1, hp=2,
             attack=ClawAttack(numdice=2, dietype=8, speed=-1, attacktext="CRAB... BATTLE")),
        Part("Tentacle", "A big, purple, %(adjective)s tentacle.", "ceph", hp=5,
             attack=BeatAttack(attacktext="%(owner)s tries to attack %(target)s with an enormous tentacle! But in a totally non-sexual way.", damage=1)),
    ]
}
