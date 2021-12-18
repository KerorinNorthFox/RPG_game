import random, math

class Character(object):
    # 物理攻撃処理 : 安定した攻撃 : 攻撃力 - (防御力 + 0~物理防御値間の乱数) : ダメージが0の場合攻撃力×0~10%のダメージ
    def physicalAttack(self, Atked):
        # ミス確率
        miss_prob = []
        for _ in range(2): miss_prob.append(random.randint(0, math.floor(Atked.speed/10)))
        # ミス処理
        if miss_prob[0] == miss_prob[1]:
            print(">>ミス")
            return
        # 物理ダメージ計算
        dmg = self.str - (Atked.vtl + random.randint(0, Atked.antiAttack))
        # カスダメ計算
        if dmg <= 0: dmg = math.floor(self.str * (random.randint(0, 10)/100))
        # クリティカル処理
        dmg, text = self._critical(dmg)
        # HP減算
        Atked.hp -= dmg
        print(f"\n>>{self.charaName}の攻撃\n{text}")
        print(f">>{self.charaName}は{Atked.charaName}に{dmg}のダメージを与えた")
        # 死亡処理
        self._noHp(Atked)

    # 魔法攻撃処理 : ダメージが通りやすいが外しやすい : 魔力 - 0~魔法防御値間の乱数 : ダメージが0の場合ノーダメ
    def magicalAttack(self, Atked):
        # 魔法ダメージ計算
        dmg = self.mana - (random.randint(0, Atked.antiMana))
        # ミス確率
        miss_prob = []
        for _ in range(2): miss_prob.append(random.randint(0, math.floor(Atked.speed/20)))
        # ミス処理
        if miss_prob[0] == miss_prob[1] or dmg <= 0:
            print(">>ミス")
            return
        # クリティカル処理
        dmg, text = self._critical(dmg)
        # HP減算
        Atked.hp -= dmg
        print(f"\n>>{self.charaName}の攻撃 \n{text}")
        print(f">>{self.charaName}は{Atked.charaName}に{dmg}のダメージを与えた")
        # 死亡処理
        self._noHp(Atked)

    # 死亡処理
    def _noHp(self, Atked):
        if Atked.hp <= 0:
            Atked.hp = 0
            Atked.alive = False
            print(f"\n>>{Atked.charaName}は倒れた")

    # クリティカル処理
    def _critical(self, dmg):
        # クリティカル確率 : 1%
        critical = random.randint(0, 100)
        # クリティカル処理
        if critical == 1:
            text = '\n>>急所にあたった!\n'
            dmg = dmg * 2
        else: text = ''
        return dmg, text

class PartyClass(Character):
    def __init__(self, charaName, job, hp, mp, str, vtl, mana, antiAttack, antiMana, speed, alive):
        self.charaName = charaName
        self.job = job
        self.hp = hp
        self.mp = mp
        self.str = str
        self.vtl = vtl
        self.mana = mana
        self.antiAttack = antiAttack
        self.antiMana = antiMana
        self.speed = speed
        self.alive = alive

    # ステータス表示
    def showStatus(self):
        print(f'''--------------------
>>Name: {self.charaName}
>>Job: {self.job}
>>HP: {self.hp}
>>MP: {self.mp}
>>STR: {self.str}
>>VTL: {self.vtl}
>>Mana: {self.mana}
>>AATK: {self.antiAttack}
>>AMana: {self.antiMana}
>>Speed: {self.speed}
''')

class EnemyClass(Character):
    def __init__(self, charaName, job, hp, mp, str, vtl, mana, antiAttack, antiMana, speed, alive, way_type):
        self.charaName = charaName
        self.job = job
        self.hp = hp
        self.mp = mp
        self.str = str
        self.vtl = vtl
        self.mana = mana
        self.antiAttack = antiAttack
        self.antiMana = antiMana
        self.speed = speed
        self.alive = alive
        self.way_type = way_type
    
    # ステータス表示
    def showStatus(self):
        print(f'''--------------------
>>Name: {self.charaName}
>>Job: {self.job}
>>HP: {self.hp}
>>MP: {self.mp}
''')
