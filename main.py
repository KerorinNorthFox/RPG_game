from CharacterClass import Character

charaA = Character("A", 100, 0, 50, 10, 40, 5, 10)
charaB = Character("B", 200, 0, 50, 10, 40, 5, 10)

charaA.magicalAttack(charaB)
charaA.showStatus()
charaB.showStatus()
print("############################")
charaB.magicalAttack(charaA)
charaA.showStatus()
charaB.showStatus()
