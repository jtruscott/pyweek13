import random
from math import floor

#these are MINIMUM values for attacks in their associated brackets
global t0_attack, t1_attack, t2_attack, t3_attack, t4_attack, attack_tiers
[t0_attack, t1_attack, t2_attack, t3_attack, t4_attack] = [1,10,20,30,40]
attack_tiers=[t0_attack, t1_attack, t2_attack, t3_attack, t4_attack]

def power_calc(numdice, dietype, damage, speed, name):
    # (1 + N)*(N/2)
    avg_die_value = ((1+dietype)*(dietype/2.0))  #average result of one die of dietype
    avg_dmg = ((avg_die_value * numdice) + damage)
    dpt = (avg_dmg / speed)
    i = len(attack_tiers)-1
    if __name__ != "__main__":
        if dpt > 50:
            log.debug("greater than 50 dpt error in" + name)
    while i >= 0:
        
        if dpt > attack_tiers[i]:
            return i
        i -= 1
        if i < 0:
            log.debug("less than 0 dpt error in" + name)
            return 0
            
class Attack:
    name = "Attack"
    base_speed = 4
    base_cooldown = 2
    base_accuracy = 0
    sound = None
    def __init__(self,
                numdice=None, dietype=None, damage=0,
                accuracy=0, status=None,
                cooldown=None, speed=0,
                attacktext="%(owner)s attacks %(target)s with an unhandled exception!"
                ):
        '''
        numdice and dietype are signed ints which replace, but do not modify, the base XdY damage of the attack;
        thus, an attack with base damage 2d4 with numdice 3 and dietype 3 would instead do 3d3.
        Values of 0 do not change the default (nor do negative values, although god knows why they'd be used).
        
        damage is just a static plus to damage - the z in XdY+Z. Note that none of the default attack profiles have a +damage.
        accuracy is bonus to-hit, status is the status effect (by name) that can proc from the attack.
        cooldown is a replacement of the calculated default
        speed is signed int modifier to the default value, not a replacement;
        remember that an increase in the value of speed makes the attack slower.
        
        attacktext is the text printed when you attack with the weapon; the default value should not be needed;
        ideally custom attack text should have been passed with the attack profile in the part profile.
         '''
        cooldown_divisor = 4    #fuck with this as needed - it all rounds and converts to int in the end, anyways)
         
        if numdice is not None:
            self.numdice = numdice
        else:
            self.numdice = self.base_numdice
        
        if dietype is not None:            
            self.dietype = dietype
        else:
            self.dietype = self.base_dietype
            
        if cooldown is not None:
            self.cooldown = cooldown
        else:
            self.cooldown = int(max(floor((self.numdice + self.dietype)/cooldown_divisor),1))
            
        self.damage = damage
        
        self.accuracy = accuracy + self.base_accuracy
        
        self.base_status = None
        if status is not None:
            self.status = status
        
        #self.cooldown = cooldown + self.base_cooldown
        if self.cooldown < 1:
            self.cooldown = 1
        
        self.speed = speed + self.base_speed
        if self.speed < 1:
            self.speed = 1
            
        self.power = power_calc(self.numdice, self.dietype, self.damage, self.speed, self.name)
        
        self.attacktext = attacktext
    
    def battle_reset(self):
        self.cur_cooldown = 0

    def battle_tick(self):
        if self.cur_cooldown:
            self.cur_cooldown -= 1
        
    def calc_min_damage(self, owner):
        return self.numdice + self.damage

    def calc_max_damage(self, owner):
        return self.numdice*self.dietype + self.damage

    def calc_damage(self, owner):
        return sum([random.randint(1,self.dietype) for d in range(self.numdice)])

    def calc_accuracy(self, owner):
        return self.accuracy + self.damage

class PunchAttack(Attack):
    name = "Punch"
    base_numdice = 1
    base_dietype = 4
    base_cooldown = 1
    base_speed = 4
    sound = 'punch'
    
class BiteAttack(Attack):
    name = "Bite"
    base_numdice = 1
    base_dietype = 6
    base_cooldown = 1
    base_speed = 5
    
class EnergyAttack(Attack):
    name = "Fry"
    base_numdice = 4
    base_dietype = 3
    base_cooldown = 5
    base_speed = 2
    sound = 'fry'

class StabAttack(Attack):
    name = "Stab"
    base_numdice = 1
    base_dietype = 4
    base_cooldown = 3
    base_speed = 4
    
class BladeAttack(Attack):
    name = "Slash"
    base_numdice = 1
    base_dietype = 4
    base_cooldown = 2
    base_speed = 3
    
class BeatAttack(Attack):
    name = "Bludgeon"
    base_numdice = 1
    base_dietype = 4
    base_cooldown = 3
    base_speed = 4
    
class TrampleAttack(Attack):
    name = "Trample"
    base_numdice = 4
    base_dietype = 3
    base_cooldown = 4
    base_speed = 4
    
class ClawAttack(Attack):
    name = "Rend"
    base_numdice = 1
    base_dietype = 6
    base_cooldown = 1
    base_speed = 3
    
    
if __name__ == "__main__":
    foo = StabAttack(dietype=8,attacktext="%(owner)s stabs at %(target)s with a great scorpion tail!")
    print foo.cooldown
    print foo.power
    foo = StabAttack(dietype=90,numdice=50,)
    print foo.cooldown
    print foo.power
    print t0_attack, t1_attack, t2_attack, t3_attack, t4_attack
    
    