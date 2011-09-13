class Attack:
    name = "Attack"
    
    def __init__(self,
                numdice=None, dietype=None, damage=0,
                accuracy=0, status=None,
                cooldown=0, speed=0
                ):
        '''
        numdice and dietype are signed ints which replace, but do not modify, the base XdY damage of the attack;
        thus, an attack with base damage 2d4 with numdice 3 and dietype 3 would instead do 3d3.
        Values of 0 do not change the default (nor do negative values, although god knows why they'd be used).
        
        damage is just a static plus to damage - the z in XdY+Z. Note that none of the default attack profiles have a +damage.
        accuracy is bonus to-hit, status is the status effect (by name) that can proc from the attack.
        cooldown and speed are signed int modifiers to default values, not replacements;
        remember that an increase in the value of speed makes the attack slower.
         '''
        if numdice is not None:
            self.numdice = numdice
        else:
            self.numdice = self.base_numdice
        
        if dietype is not None:            
            self.dietype = dietype
        else:
            self.dietype = self.base_dietype
            
        self.damage = damage
        
        self.base_accuracy = 0
        self.accuracy = accuracy + self.base_accuracy
        
        self.base_status = None
        if status is not None:
            self.status = status
        
        self.base_cooldown = 2      #this shouldn't be used, but just in case
        self.cooldown = cooldown + self.base_cooldown
        
        self.base_speed = 4         #this shouldn't be used, but just in case
        self.speed = speed + self.base_speed

    def calc_min_damage(self, owner):
        return self.numdice + self.damage

    def calc_max_damage(self, owner):
        return self.numdice*self.dietype + self.damage

    def calc_accuracy(self, owner):
        return self.accuracy + self.damage

class PunchAttack(Attack):
    name = "Punch"
    base_numdice = 1
    base_dietype = 4
    base_cooldown = 1
    base_speed = 4
    
class BiteAttack(Attack):
    name = "Bite"
    base_numdice = 1
    base_dietype = 6
    base_cooldown = 1
    base_speed = 5
    
class LaserAttack(Attack):
    name = "Laser"
    base_numdice = 4
    base_dietype = 3
    base_cooldown = 6
    base_speed = 2
