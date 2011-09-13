class Attack:
    name = "Attack"
    
    def __init__(self,
                numdice=0, dietype=0, damage=0,
                # x and y are unsigned ints which replace, but do not modify, the base XdY damage of the attack;
                # thus, an attack with base damage 2d4 with numdice 3 and dietype 3 would instead do 3d3.
                # values of 0 do not change the default (nor do negative values, although god knows why they'd be used)
                # Damage is just a static plus to damage - the z in XdY+Z. Note that none of the default attack profiles have a +damage.
                accuracy=0, status=None,
                # accuracy is bonus to-hit, status is the status effect (by name) that can proc from the attack
                cooldown=0, speed=0
                # these are signed int modifiers to default values, not replacements;
                # remember that an increase in the value of speed makes the attack slower.
                ):
        if numdice > 0:
            self.numdice = numdice
            
        if numdice > 0:
            self.dietype = dietype
            
        self.damage = damage
        self.accuracy += accuracy
        self.status = status
        self.cooldown += cooldown
        self.speed += speed
        

class PunchAttack(Attack):
    name = "Punch"
    numdice = 1
    dietype = 4
    cooldown = 1
    speed = 4
    
class BiteAttack(Attack):
    name = "Bite"
    numdice = 1
    dietype = 6
    cooldown = 1
    speed = 5
    
class LaserAttack(Attack):
    name = "Laser"
    numdice = 4
    dietype = 3
    cooldown = 6
    speed = 2 