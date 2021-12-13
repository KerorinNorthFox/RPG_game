import random, math

class Character(object):
    def __init__(self, charaName, hp, mp, atk, vtl, mana, antiAttack, antiMana):
        print(f"character {charaName} is born")
        self.charaName = charaName
        self.hp = hp
        self.mp = mp
        self.atk = atk
        self.vtl = vtl
        self.mana = mana
        self.antiAttack = antiAttack
        self.antiMana = antiMana

    def showStatus(self):
        print(f'''--------------------
>>Name: {self.charaName}
>>MP: {self.mp}
>>HP: {self.hp}
>>Power: {self.atk}
>>Vitality: {self.vtl}
-------------------
''')

    # 物理攻撃処理 : 安定した攻撃 : 攻撃力 - (防御力 + 0~物理防御値間の乱数) : ダメージが0の場合攻撃力×0~10%のダメージ
    def physicalAttack(self, atked):
        dmg = self.atk - (atked.vtl + random.randint(0, atked.antiAttack))
        dmg = math.floor(self.atk * (random.randint(0, 10)/100)) if dmg <= 0 else dmg
        atked.hp -= dmg
        print(f">>{atked.charaName} is damaged {dmg} by {self.charaName}")

    # 魔法攻撃処理 : ダメージが通りやすいが外しやすい : 魔力 - 0~魔法防御値間の乱数 : ダメージが0の場合ノーダメ
    def magicalAttack(self, atked):
        beforeHp = atked.hp
        dmg = self.mana - (random.randint(0, atked.antiMana))
        dmg = 0 if dmg <= 0 else dmg
        atked.hp -= dmg
        print(f">>{atked.charaName} is damaged {dmg} by {self.charaName}")



