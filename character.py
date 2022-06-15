from colorama import Back
import random
import math
import time
import os

import streamtextmodule as stm


PARTITION: str = '-------------------------'
TIME: float = 1.5
CLEAR = 'cls' if os.name == 'nt' else 'clear' # 実行os判別


class Character(object): # DONE
    # 物理攻撃処理 : 安定した攻撃 : 攻撃力 - (防御力 + 0~物理防御値間の乱数) : ダメージが0の場合、攻撃力×1~10%のダメージ
    def physical_attack(self, Atked:object, defence:bool) -> None:
        stm.stream_text(f"\n>>{self.name}の攻撃")
        # ミス確率
        miss_prob: list[int] = self._miss_calc(Atked, 10)
        # ミス処理
        if miss_prob[0] == miss_prob[1]:
            time.sleep(TIME)
            stm.stream_text(">>ミス")
            return
        # 物理ダメージ計算
        dmg: int = self.str - (Atked.vtl + random.randint(0, Atked.aatk))
        # カスダメ計算
        if dmg <= 0:
            dmg = math.floor(self.str * (random.randint(1, 10)/100))
        # クリティカル処理
        dmg, text = self._critical(dmg)
        # HP減算
        self._hp_subtraction(defence, Atked, dmg, text)
        # 死亡処理
        self._no_hp(Atked)

    # 魔法攻撃処理 : ダメージが通りやすい(防御貫通)が外しやすい : 魔力 - 0~魔法防御値間の乱数 : ダメージが0の場合ノーダメ
    def magical_attack(self, Atked:object, defence:bool, rate:float) -> None:
        stm.stream_text(f"\n>>{self.name}の攻撃")
        # 魔法ダメージ計算
        dmg: int = math.floor(self.mana * rate) - (random.randint(0, Atked.amana))
        # ミス確率
        miss_prob: list[int] = self._miss_calc(Atked, 20)
        # ミス処理
        if miss_prob[0] == miss_prob[1] or dmg <= 0:
            time.sleep(TIME)
            stm.stream_text("\n>>ミス")
            return
        # クリティカル処理
        dmg, text = self._critical(dmg)
        # HP減算
        self._hp_subtraction(defence, Atked, dmg, text)
        # 死亡処理
        self._no_hp(Atked)

    # ヒール
    def heal(self, Healed:object, rate:float):
        stm.stream_text(f"\n>>{self.name}のヒール")
        if Healed.hp == Healed.hp_backup:
            stm.stream_text('>>これ以上回復できない')
            return
        heal: int = math.floor((self.mana/3) * rate)
        Healed.hp += heal
        if Healed.hp >= Healed.hp_backup: 
            Healed.hp = Healed.hp_backup
            stm.stream_text(f"\n>>{Healed.name}の体力が最大まで回復した")
        else:
            stm.stream_text(f"\n>>{Healed.name}の体力が{heal}回復した")

    # ミス確率計算 : 0~スピード/xの間でランダム値を二つ取り、一致した場合ミス
    def _miss_calc(self, Atked:object, x:int) -> list[int]:
        miss_prob: list[int] = []
        for _ in range(2):
            miss_prob.append(random.randint(0, math.floor(Atked.speed/x)))
        return miss_prob

    # クリティカル処理 確率 : 1%
    def _critical(self, dmg:int) -> int | str:
        critical: int = random.randint(0, 100)
        # クリティカル処理
        if critical == 1:
            text: str = '\n>>急所にあたった!\n'
            dmg = math.float(dmg * 1.6)
        else:
            text: str = ''
        return dmg, text

    # hp減算
    def _hp_subtraction(self, defence:bool, Atked:object, dmg:int, text:str) -> None:
        if defence:
            dmg = math.floor(dmg/6) # 防御時ダメージ1/6
            Atked.hp -= dmg
            print('nya')
        else:
            Atked.hp -= dmg
        time.sleep(TIME)
        stm.stream_text(f"{text}>>{self.name}は{Atked.name}に{dmg}のダメージを与えた")
    
    # 死亡処理
    def _no_hp(self, Atked:object) -> None:
        if Atked.hp <= 0:
            Atked.hp = 0
            Atked.alive = False
            time.sleep(TIME)
            stm.stream_text(f"\n>>{Atked.name}は倒れた")


class PartyClass(Character): # DONE
    def __init__(self, name, job, hp, mp, 
                 strg, vtl, mana, aatk, 
                 amana, speed, alive, element, magic) -> None:
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
        self.magic: list[str] = magic
        self.way: int = 0
        self.target: int = 0
        self.selected_magic: int = None
        self.defence: bool = False
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
    def show_status(self) -> None:
        print(f'''----------------------------------------
>>Name: {self.name}
>>Job: {self.job}
>>Level: {self.level} | 次のレベルまであと{self.basic_exp*self.level-self.my_exp}exp''')
        if self.element:
            print(">>Element: 光")
        else:
            print(">>Element: 闇")
        if self.hp == 0:
            print(f">>HP: {Back.RED + str(self.hp)} / {str(self.hp_backup) + Back.RESET}")
        else:
            print(f">>HP: {self.hp} / {self.hp_backup}")
        print(f'''>>MP: {self.mp} / {self.mp_backup}
>>STR: {self.str} / {self.str_backup}
>>VTL: {self.vtl} / {self.vtl_backup}
>>Mana: {self.mana} / {self.mana_backup}
>>AATK: {self.aatk} / {self.aatk_backup}
>>AMana: {self.amana} / {self.aatk_backup}
>>Speed: {self.speed} / {self.speed_backup}
''')

    # 経験値加算
    def add_exp(self, exp:int) -> None:
        # 加算
        self.my_exp += exp
        while(True):
            # レベルアップ処理
            if self.my_exp >= self.basic_exp*self.level:
                print(PARTITION)
                stm.stream_text(f'>>{self.name}はレベルアップした!')
                stm.stream_text(f'>>Level{self.level} → {self.level+1}')
                self._add_to_status()
                self._levelup_status_show()
                time.sleep(TIME)
                self.my_exp -= self.basic_exp*self.level
                self.level += 1
            else:
                break

    # ステータス加算
    def _add_to_status(self) -> None:
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
    def _levelup_status_show(self) -> None:
        stm.stream_text(f'''>>HP: {self.hp_backup} (↑10)
>>MP: {self.mp_backup} (↑4)
>>STR: {self.str_backup} (↑10)
>>VTL: {self.vtl_backup} (↑8)
>>Mana: {self.mana_backup} (↑10)
>>AATK: {self.aatk_backup} (↑3)
>>AMana: {self.amana_backup} (↑3)
>>Speed: {self.speed_backup} (↑5)
''', sleep_time=0.01)

    # ポイント振り分け
    def skillpoint_assign(self, status_select:int, num:int) -> None:
        if status_select == 1:
            self.hp += num
            self.hp_backup += num
        elif status_select == 2:
            self.mp += num
            self.mp_backup += num
        elif status_select == 3:
            self.str += num
            self.str_backup += num
        elif status_select == 4:
            self.vtl += num
            self.vtl_backup += num
        elif status_select == 5:
            self.mana += num
            self.mana_backup += num
        elif status_select == 6:
            self.aatk += num
            self.aatk_backup += num
        elif status_select == 7:
            self.amana += num
            self.amana_backup += num
        elif status_select == 8:
            self.speed += num
            self.speed_backup += num


class EnemyClass(Character): # DONE
    def __init__(self, name, job, hp, mp, 
                 strg, vtl, mana, aatk, amana, 
                 speed, alive, element, way_type) -> None:
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
    def show_status(self) -> None:
        print(f'''----------------------------------------
>>Name: {self.name}
>>Job: {self.job}''')
        if self.element:
            print(">>Element: 光")
        else:
            print(">>Element: 闇")
        if self.hp == 0:
            print(f">>HP: {Back.RED + str(self.hp)} / {str(self.hp_backup) + Back.RESET}")
        else:
            print(f">>HP: {self.hp} / {self.hp_backup}")
        print(f'''>>MP: {self.mp} / {self.mp_backup}
>>STR: {self.str} / {self.str_backup}
>>VTL: {self.vtl} / {self.vtl_backup}
>>Mana: {self.mana} / {self.mana_backup}
>>AATK: {self.aatk} / {self.aatk_backup}
>>AMana: {self.amana} / {self.aatk_backup}
>>Speed: {self.speed} / {self.speed_backup}
''')

