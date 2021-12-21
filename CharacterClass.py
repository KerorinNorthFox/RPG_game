import random, math, time
from bs4 import element
from colorama import Back

TIME = 2

class Character(object):
    # 物理攻撃処理 : 安定した攻撃 : 攻撃力 - (防御力 + 0~物理防御値間の乱数) : ダメージが0の場合攻撃力×0~10%のダメージ
    def physicalAttack(self, Atked, defence):
        print(f"\n>>{self.charaName}の攻撃")
        # ミス確率
        miss_prob = []
        for _ in range(2): miss_prob.append(random.randint(0, math.floor(Atked.speed/10)))
        # ミス処理
        if miss_prob[0] == miss_prob[1]:
            time.sleep(TIME)
            print(">>ミス")
            return
        # 物理ダメージ計算
        dmg = self.str - (Atked.vtl + random.randint(0, Atked.antiAttack))
        # カスダメ計算
        if dmg <= 0: dmg = math.floor(self.str * (random.randint(0, 10)/100))
        # クリティカル処理
        dmg, text = self._critical(dmg)
        # HP減算
        if defence is True: Atked.hp -= math.floor(dmg/10) # 防御時ダメージ1/5
        else: Atked.hp -= dmg
        time.sleep(TIME)
        print(f"\n{text}>>{self.charaName}は{Atked.charaName}に{dmg}のダメージを与えた")
        # 死亡処理
        self._noHp(Atked)

    # 魔法攻撃処理 : ダメージが通りやすいが外しやすい : 魔力 - 0~魔法防御値間の乱数 : ダメージが0の場合ノーダメ
    def magicalAttack(self, Atked, defence, rate):
        print(f"\n>>{self.charaName}の攻撃")
        # 魔法ダメージ計算
        dmg = math.floor(self.mana * rate) - (random.randint(0, Atked.antiMana))
        # ミス確率
        miss_prob = []
        for _ in range(2): miss_prob.append(random.randint(0, math.floor(Atked.speed/20)))
        # ミス処理
        if miss_prob[0] == miss_prob[1] or dmg <= 0:
            time.sleep(TIME)
            print("\n>>ミス")
            return
        # クリティカル処理
        dmg, text = self._critical(dmg)
        # HP減算
        if defence is True: Atked.hp -= math.floor(dmg/10) # 防御時ダメージ1/5
        else: Atked.hp -= dmg
        time.sleep(TIME)
        print(f"\n{text}>>{self.charaName}は{Atked.charaName}に{dmg}のダメージを与えた")
        # 死亡処理
        self._noHp(Atked)

    def heal(self, Healed, rate):
        print(f"\n>>{self.charaName}のヒール")
        heal = math.floor((self.mana/3) * rate)
        Healed.hp += heal
        if Healed.hp >= Healed.hp_BU: 
            Healed.hp == Healed.hp_BU
            print(f"\n>>{Healed.charaName}の体力が最大まで回復した")
        else: print(f"\n>>{Healed.charaName}の体力が{heal}回復した")

    # 死亡処理
    def _noHp(self, Atked):
        if Atked.hp <= 0:
            Atked.hp = 0
            Atked.alive = False
            time.sleep(TIME)
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
    def __init__(self, charaName, job, hp, mp, str, vtl, mana, antiAttack, antiMana, speed, alive, element, magic):
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
        self.element = element
        self.magic = magic
        self.way = 0
        self.target = 0
        self.my_magic = 0
        # バックアップ
        self.hp_BU = hp
        self.mp_BU = mp
        self.str_BU = str
        self.vtl_BU = vtl
        self.mana_BU = mana
        self.antiAttack_BU = antiAttack
        self.antiMana_BU = antiMana
        self.speed_BU = speed

    # ステータス表示
    def showStatus(self):
        print(f'''--------------------
>>Name: {self.charaName}
>>Job: {self.job}''')
        if self.hp == 0:
            print(f">>HP: {Back.RED + str(self.hp)} / {str(self.hp_BU) + Back.RESET}")
        else:
            print(f">>HP: {self.hp} / {self.hp_BU}")
        print(f'''>>MP: {self.mp} / {self.mp_BU}
>>STR: {self.str} / {self.str_BU}
>>VTL: {self.vtl} / {self.vtl_BU}
>>Mana: {self.mana} / {self.mana_BU}
>>AATK: {self.antiAttack} / {self.antiAttack_BU}
>>AMana: {self.antiMana} / {self.antiMana_BU}
>>Speed: {self.speed} / {self.speed_BU}
''')

class EnemyClass(Character):
    def __init__(self, charaName, job, hp, mp, str, vtl, mana, antiAttack, antiMana, speed, alive, way_type, element):
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
        self.element = element
        self.way_type = way_type
        self.way = 0
        self.target = 0
        # バックアップ
        self.hp_BU = hp
        self.mp_BU = mp
        self.str_BU = str
        self.vtl_BU = vtl
        self.mana_BU = mana
        self.antiAttack_BU = antiAttack
        self.antiMana_BU = antiMana
        self.speed_BU = speed
        self.way_type_BU = way_type
    
    # ステータス表示
    def showStatus(self):
        print(f'''--------------------
>>Name: {self.charaName}
>>Job: {self.job}''')
        if self.hp == 0:
            print(f">>HP: {Back.RED + str(self.hp)} / {str(self.hp_BU) + Back.RESET}")
        else:
            print(f">>HP: {self.hp} / {self.hp_BU}")
        print(f">>MP: {self.mp} / {self.mp_BU}")
