class Attack:
    name = "Attack"
    
    def __init__(self,
                size=1, count=4, bonus=0,
                accuracy=0):

        self.size = size
        self.count = count
        self.bonus = bonus

        self.accuracy = accuracy

class PunchAttack(Attack):
    name = "Punch"
