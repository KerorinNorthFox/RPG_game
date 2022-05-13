from colorama import Back
import random, math, time
import StreamTextModule as stm

PARTITION: str = '-------------------------'
TIME: float = 1.5

class Character(object): # DONE
    # 物理攻撃処理 : 安定した攻撃 : 攻撃力 - (防御力 + 0~物理防御値間の乱数) : ダメージが0の場合、攻撃力×0~10%のダメージ
    def physicalAttack(self, Atked, defence):
        stm.streamText(f"\n>>{self.name}の攻撃")
        # ミス確率
        miss_prob = self._missCalc(Atked, 10)
        # ミス処理
        if miss_prob[0] == miss_prob[1]:
            time.sleep(TIME)
            stm.streamText(">>ミス")
            return
        # 物理ダメージ計算
        dmg: int = self.str - (Atked.vtl + random.randint(0, Atked.aatk))
        # カスダメ計算
        if dmg <= 0: dmg = math.floor(self.str * (random.randint(0, 10)/100))
        # クリティカル処理
        dmg, text = self._critical(dmg)
        # HP減算
        self._hpSubtraction(defence, Atked, dmg, text)
        # 死亡処理
        self._noHp(Atked)

    # 魔法攻撃処理 : ダメージが通りやすい(防御貫通)が外しやすい : 魔力 - 0~魔法防御値間の乱数 : ダメージが0の場合ノーダメ
    def magicalAttack(self, Atked, defence, rate):
        stm.streamText(f"\n>>{self.name}の攻撃")
        # 魔法ダメージ計算
        dmg: int = math.floor(self.mana * rate) - (random.randint(0, Atked.amana))
        # ミス確率
        miss_prob = self._missCalc(Atked, 20)
        # ミス処理
        if miss_prob[0] == miss_prob[1] or dmg <= 0:
            time.sleep(TIME)
            stm.streamText("\n>>ミス")
            return
        # クリティカル処理
        dmg, text = self._critical(dmg)
        # HP減算
        self._hpSubtraction(defence, Atked, dmg, text)
        # 死亡処理
        self._noHp(Atked)

    # ミス確率計算 : スピード/xでランダム値を二つ取り、一致した場合ミス
    def _missCalc(self, Atked, x):
        miss_prob: list[int] = []
        for _ in range(2): miss_prob.append(random.randint(0, math.floor(Atked.speed/x)))
        return miss_prob

    # クリティカル処理 確率 : 1%
    def _critical(self, dmg):
        critical: int = random.randint(0, 100)
        # クリティカル処理
        if critical == 1:
            text = '\n>>急所にあたった!\n'
            dmg = dmg * 1.6
        else: text = ''
        return dmg, text

    # hp減算
    def _hpSubtraction(self, defence, Atked, dmg, text):
        if defence is True:
            dmg = math.floor(dmg/10) # 防御時ダメージ1/10
            Atked.hp -= dmg
            print('nya')
        else: Atked.hp -= dmg
        time.sleep(TIME)
        stm.streamText(f"\n{text}>>{self.name}は{Atked.name}に{dmg}のダメージを与えた")
    
    # 死亡処理
    def _noHp(self, Atked):
        if Atked.hp <= 0:
            Atked.hp = 0
            Atked.alive = False
            time.sleep(TIME)
            stm.streamText(f"\n>>{Atked.name}は倒れた")

class PartyClass(Character): # DONE
    def __init__(self, name, job, hp, mp, strg, vtl, mana, aatk, amana, speed, alive, element):
        self.name: str = name
        self.job: str = job
        self.level: int = 1
        self.my_exp: int = 0
        self.basic_exp: int = 100
        self.hp: int = hp
        self.mp: int = mp
        self.str: int = strg
        self.vtl: int = vtl
        self.mana: int = mana
        self.aatk: int = aatk
        self.amana: int = amana
        self.speed: int = speed
        self.alive: bool = alive
        self.element: bool = element
        self.way: int = 0
        self.target: int = 0
        # バックアップ
        self.hp_backup: int = hp
        self.mp_backup: int = mp
        self.str_backup: int = strg
        self.vtl_backup: int = vtl
        self.mana_backup: int = mana
        self.aatk_backup: int = aatk
        self.amana_backup: int = amana
        self.speed_backup: int = speed

    # ステータス表示
    def showStatus(self):
        print(f'''--------------------
>>Name: {self.name}
>>Job: {self.job}
>>Level: {self.level} | 次のレベルまであと{self.basic_exp*self.level-self.my_exp}exp''')
        if self.element is True: print(">>Element: 光")
        else: print(">>Element: 闇")
        if self.hp == 0: print(f">>HP: {Back.RED + str(self.hp)} / {str(self.hp_backup) + Back.RESET}")
        else: print(f">>HP: {self.hp} / {self.hp_backup}")
        print(f'''>>MP: {self.mp} / {self.mp_backup}
>>STR: {self.str} / {self.str_backup}
>>VTL: {self.vtl} / {self.vtl_backup}
>>Mana: {self.mana} / {self.mana_backup}
>>AATK: {self.aatk} / {self.aatk_backup}
>>AMana: {self.amana} / {self.aatk_backup}
>>Speed: {self.speed} / {self.speed_backup}
''')

    # 経験値加算
    def addExp(self, World):
        # 加算
        self.my_exp += World.exp
        while(True):
            # レベルアップ処理
            if self.my_exp >= self.basic_exp*self.level:
                print(PARTITION)
                stm.streamText(f'>>{self.name}はレベルアップした!')
                stm.streamText(f'>>Level{self.level} → {self.level+1}')
                self._addToStatus()
                self._levelupStatusShow()
                time.sleep(TIME)
                self.my_exp -= self.basic_exp*self.level
                self.level += 1
            else: break

    # ステータス加算
    def _addToStatus(self):
        self.hp += 10
        self.hp_backup += 10
        if self.mp_backup != 0:
            self.mp += 4
            self.mp_backup += 4
        if self.str_backup != 0:
            self.str += 10
            self.str_backup += 10
        if self.vtl_backup != 0:
            self.vtl += 8
            self.vtl_backup += 8
        if self.mana_backup != 0:
            self.mana += 10
            self.mana_backup += 10
        if self.aatk_backup != 0:
            self.aatk += 3
            self.aatk_backup += 3
        if self.amana_backup != 0:
            self.amana += 3
            self.amana_backup += 3
        if self.speed_backup != 0:
            self.speed += 5
            self.speed_backup += 5

    # レベルアップ時ステータス表示
    def _levelupStatusShow(self):
        stm.streamText(f'''>>HP: {self.hp_backup} (↑10)
>>MP: {self.mp_backup} (↑4)
>>STR: {self.str_backup} (↑10)
>>VTL: {self.vtl_backup} (↑8)
>>Mana: {self.mana_backup} (↑10)
>>AATK: {self.aatk_backup} (↑3)
>>AMana: {self.amana_backup} (↑3)
>>Speed: {self.speed_backup} (↑5)
''', sleep_time=0.01)

    # ポイント振り分け
    def pointAssign(self, status_select, num):
        status = [self.hp, self.mp, self.str, self.vtl, self.mana, self.antiAttack, self.antiMana, self.speed]
        status_backup = [self.hp_backup, self.mp_backup, self.str_backup, self.vtl_backup, self.mana_backup, self.aatk_backup, self.amana_backup, self.speed_backup]
        # 振り分け
        status[status_select-1] += num
        status_backup[status_select-1] += num

class EnemyClass(Character): # DONE
    def __init__(self, name, job, hp, mp, strg, vtl, mana, aatk, amana, speed, alive, element, way_type):
        self.name: str = name
        self.job: str = job
        self.hp: int = hp
        self.mp: int = mp
        self.str: int = strg
        self.vtl: int = vtl
        self.mana: int = mana
        self.aatk: int = aatk
        self.amana: int = amana
        self.speed: int = speed
        self.alive: bool = alive
        self.element: bool = element
        self.way_type: int = way_type
        self.way: int = 0
        self.target: int = 0
        # バックアップ
        self.hp_backup: int = hp
        self.mp_backup: int = mp
        self.str_backup: int = strg
        self.vtl_backup: int = vtl
        self.mana_backup: int = mana
        self.aatk_backup: int = aatk
        self.amana_backup: int = amana
        self.speed_backup: int = speed

    # ステータス表示
    def showStatus(self):
        print(f'''--------------------
>>Name: {self.name}
>>Job: {self.job}''')
        if self.element is True: print(">>Element: 光")
        else: print(">>Element: 闇")
        if self.hp == 0: print(f">>HP: {Back.RED + str(self.hp)} / {str(self.hp_backup) + Back.RESET}")
        else: print(f">>HP: {self.hp} / {self.hp_backup}")
        print(f'''>>MP: {self.mp} / {self.mp_backup}
>>STR: {self.str} / {self.str_backup}
>>VTL: {self.vtl} / {self.vtl_backup}
>>Mana: {self.mana} / {self.mana_backup}
>>AATK: {self.aatk} / {self.aatk_backup}
>>AMana: {self.amana} / {self.aatk_backup}
>>Speed: {self.speed} / {self.speed_backup}
''')