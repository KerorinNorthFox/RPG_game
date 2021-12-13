from CharacterClass import Character

PARTITION = '-------------------------'
ONEONE = True
ONETWO = False

class Battle:
    def __init__(self, Party, Stage):
        pass

class Stages:
    def showStage(self):
        print(PARTITION)

    def oneOne(self):
        Enemy = Character("EnemyA", "Zombie", 50, 0, 10, 5, 0, 0, 0)
        return Enemy

    def oneTwo(self):
        Enemy = []
        Enemy.append(Character("EnemyA", "Zombie", 50, 0, 10, 5, 0, 0, 0))
        Enemy.append(Character("EnemyB", "Zombie", 50, 0, 10, 5, 0, 0, 0))
        return Enemy

if __name__ == "__main__":
    while(True):    
        print("Select the stage : ")
