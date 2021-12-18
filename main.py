from CharacterClass import *

charaA = PartyClass("A", "unkown", 100, 0, 50, 10, 40, 5, 10, 100, True)
charaB = EnemyClass("B", "unkown", 200, 0, 50, 10, 40, 5, 10, 100, True, 1)

charaA.physicalAttack(charaB)
charaA.showStatus()
charaB.showStatus()
print("############################")
charaB.physicalAttack(charaA)
charaA.showStatus()
charaB.showStatus()