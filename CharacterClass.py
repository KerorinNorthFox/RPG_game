import random, math, time
import StreamTextModule as stm
from colorama import Back

PARTITION: str = '-------------------------'
TIME: float = 1.5

class Character(object):
    # 物理攻撃処理 : 安定した攻撃 : 攻撃力 - (防御力 + 0~物理防御値間の乱数) : ダメージが0の場合攻撃力×0~10%のダメージ
    def physicalAttack(self, Atked, defence):
        stm.streamText(f"\n>>{self.charaName}の攻撃")
        # ミス確率
        miss_prob = self._miss_calc(Atked, 10)
        # ミス処理
        if miss_prob[0] == miss_prob[1]:
            time.sleep(TIME)
            stm.streamText(">>ミス")
            return
        # 物理ダメージ計算
        dmg: int = self.str - (Atked.vtl + random.randint(0, Atked.antiAttack))
        # カスダメ計算
        if dmg <= 0: dmg = math.floor(self.str * (random.randint(0, 10)/100))
        # クリティカル処理
        dmg, text = self._critical(dmg)
        # HP減算
        self._hp_subtraction(defence, Atked, dmg, text)
        # 死亡処理
        self._noHp(Atked)

    # 魔法攻撃処理 : ダメージが通りやすいが外しやすい : 魔力 - 0~魔法防御値間の乱数 : ダメージが0の場合ノーダメ
    def magicalAttack(self, Atked, defence, rate):
        stm.streamText(f"\n>>{self.charaName}の攻撃")
        # 魔法ダメージ計算
        dmg: int = math.floor(self.mana * rate) - (random.randint(0, Atked.antiMana))
        # ミス確率
        miss_prob = self._miss_calc(Atked, 20)
        # ミス処理
        if miss_prob[0] == miss_prob[1] or dmg <= 0:
            time.sleep(TIME)
            print("\n>>ミス")
            return
        # クリティカル処理
        dmg, text = self._critical(dmg)
        # HP減算
        self._hp_subtraction(defence, Atked, dmg, text)
        # 死亡処理
        self._noHp(Atked)

    def heal(self, Healed, rate):
        stm.streamText(f"\n>>{self.charaName}のヒール")
        if Healed.hp == Healed.hp_BU:
            stm.streamText('>>これ以上回復できない')
            return
        heal: int = math.floor((self.mana/3) * rate)
        Healed.hp += heal
        if Healed.hp >= Healed.hp_BU: 
            Healed.hp == Healed.hp_BU
            stm.streamText(f"\n>>{Healed.charaName}の体力が最大まで回復した")
        else:
            stm.streamText(f"\n>>{Healed.charaName}の体力が{heal}回復した")

    # ミス確率計算
    def _miss_calc(self, Atked, x):
        miss_prob: list[int] = []
        for _ in range(2): miss_prob.append(random.randint(0, math.floor(Atked.speed/x)))
        return miss_prob

    # hp減算
    def _hp_subtraction(self, defence, Atked, dmg, text):
        if defence is True:
            dmg = math.floor(dmg/10) # 防御時ダメージ1/10
            Atked.hp -= dmg
            print('nya')
        else: Atked.hp -= dmg
        time.sleep(TIME)
        stm.streamText(f"\n{text}>>{self.charaName}は{Atked.charaName}に{dmg}のダメージを与えた")

    # 死亡処理
    def _noHp(self, Atked):
        if Atked.hp <= 0:
            Atked.hp = 0
            Atked.alive = False
            time.sleep(TIME)
            stm.streamText(f"\n>>{Atked.charaName}は倒れた")

    # クリティカル処理
    def _critical(self, dmg):
        # クリティカル確率 : 1%
        critical: int = random.randint(0, 100)
        # クリティカル処理
        if critical == 1:
            text = '\n>>急所にあたった!\n'
            dmg = dmg * 1.6
        else: text = ''
        return dmg, text

class PartyClass(Character):
    def __init__(self, charaName, job, hp, mp, strg, vtl, mana, antiAttack, antiMana, speed, alive, element, magic):
        self.charaName: str = charaName
        self.job: str = job
        self.level: int = 1
        self.my_exp: int = 0
        self.basic_exp: int = 100
        self.hp: int = hp
        self.mp: int = mp
        self.str: int = strg
        self.vtl: int = vtl
        self.mana: int = mana
        self.antiAttack: int = antiAttack
        self.antiMana: int = antiMana
        self.speed: int = speed
        self.alive: bool = alive
        self.element: bool = element
        self.magic: list[str] = magic
        self.defence: bool = False
        self.way: int = 0
        self.target: int = 0
        self.my_magic: int = 0
        # バックアップ
        self.hp_BU = hp
        self.mp_BU = mp
        self.str_BU = strg
        self.vtl_BU = vtl
        self.mana_BU = mana
        self.antiAttack_BU = antiAttack
        self.antiMana_BU = antiMana
        self.speed_BU = speed

    # ステータス表示
    def showStatus(self):
        print(f'''--------------------
>>Name: {self.charaName}
>>Job: {self.job}
>>Level: {self.level} | 次のレベルまであと{self.basic_exp*self.level-self.my_exp}exp''')
        if self.element is True: print(">>Element: 光")
        else: print(">>Element: 闇")
        if self.hp == 0: print(f">>HP: {Back.RED + str(self.hp)} / {str(self.hp_BU) + Back.RESET}")
        else: print(f">>HP: {self.hp} / {self.hp_BU}")
        print(f'''>>MP: {self.mp} / {self.mp_BU}
>>STR: {self.str} / {self.str_BU}
>>VTL: {self.vtl} / {self.vtl_BU}
>>Mana: {self.mana} / {self.mana_BU}
>>AATK: {self.antiAttack} / {self.antiAttack_BU}
>>AMana: {self.antiMana} / {self.antiMana_BU}
>>Speed: {self.speed} / {self.speed_BU}
''')

    # 経験値加算
    def add_exp(self, World):
        # 加算
        self.my_exp += World.exp
        while(True):
            if self.my_exp >= self.basic_exp*self.level:
                print(PARTITION)
                stm.streamText(f'>>{self.charaName}はレベルアップした!')
                stm.streamText(f'>>Level{self.level} → {self.level+1}')
                self._add_to_status()
                self._levelup_status_show()
                time.sleep(TIME)
                self.my_exp -= self.basic_exp*self.level
                self.level += 1
            else: break

    # ステータス加算
    def _add_to_status(self):
        self.hp += 10
        self.hp_BU += 10
        if self.mp_BU != 0:
            self.mp += 4
            self.mp_BU += 4
        if self.str_BU != 0:
            self.str += 10
            self.str_BU += 10
        if self.vtl_BU != 0:
            self.vtl += 8
            self.vtl_BU += 8
        if self.mana_BU != 0:
            self.mana += 10
            self.mana_BU += 10
        if self.antiAttack_BU != 0:
            self.antiAttack += 3
            self.antiAttack_BU += 3
        if self.antiMana_BU != 0:
            self.antiMana += 3
            self.antiMana_BU += 3
        if self.speed_BU != 0:
            self.speed += 5
            self.speed_BU += 5

    # レベルアップ時ステータス表示
    def _levelup_status_show(self):
        stm.streamText(f'''>>HP: {self.hp_BU} (↑10)
>>MP: {self.mp_BU} (↑4)
>>STR: {self.str_BU} (↑10)
>>VTL: {self.vtl_BU} (↑8)
>>Mana: {self.mana_BU} (↑10)
>>AATK: {self.antiAttack_BU} (↑3)
>>AMana: {self.antiMana_BU} (↑3)
>>Speed: {self.speed_BU} (↑5)
''', sleep_time=0.01)
        
    # ポイント振り分け
    def point_assign(self, status_select, num):
        status = [self.hp, self.mp, self.str, self.vtl, self.mana, self.antiAttack, self.antiMana, self.speed]
        status_BU = [self.hp_BU, self.mp_BU, self.str_BU, self.vtl_BU, self.mana_BU, self.antiAttack_BU, self.antiMana_BU, self.speed_BU]
        # 振り分け
        status[status_select] += num
        status_BU[status_select] += num

class EnemyClass(Character):
    def __init__(self, charaName, job, hp, mp, strg, vtl, mana, antiAttack, antiMana, speed, alive, way_type, element):
        self.charaName: str = charaName
        self.job: str = job
        self.hp: int = hp
        self.mp: int = mp
        self.str: int = strg
        self.vtl: int = vtl
        self.mana: int = mana
        self.antiAttack: int = antiAttack
        self.antiMana: int = antiMana
        self.speed: int = speed
        self.alive: bool = alive
        self.element: bool = element
        self.way_type: int = way_type
        self.way: int = 0
        self.target: int = 0
        # バックアップ
        self.hp_BU = hp
        self.mp_BU = mp
        self.str_BU = strg
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
        if self.element is True: print(">>Element: 光")
        else: print(">>Element: 闇")
        if self.hp == 0:
            print(f">>HP: {Back.RED + str(self.hp)} / {str(self.hp_BU) + Back.RESET}")
        else:
            print(f">>HP: {self.hp} / {self.hp_BU}")
        print(f">>MP: {self.mp} / {self.mp_BU}")
