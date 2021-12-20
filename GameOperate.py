from tkinter.constants import NONE
from CharacterClass import *
import os, sys, time

TIME = 2
PARTITION = '-------------------------'
MAGICNAME = ["通常", "初級ヒール", "中級ヒール", "上級ヒール", "光"]
ONEONE = True
ONETWO = True

# 戦闘処理
class Battle(object):
    def __init__(self, Party, Enemy):
        self.PARTYLENGTH = len(Party) # 味方の人数
        self.ENEMYLENGTH = len(Enemy) # 敵の人数
        self.NOWTURN = 1

        print(">>戦闘開始\n")
        # 敵とエンカウント表示
        self._encountEnemy(Enemy) 
        # メインループ開始
        try:
            while(True):
                # 表示リセット
                os.system('cls')
                # 現在のターン表示
                print(f"\n>>現在のターン : {self.NOWTURN}\n")
                # 敵味方ステータス表示
                self._showStatuses(Party, Enemy)
                print(PARTITION*2)

                # 味方のターン
                for chara_num in range(self.PARTYLENGTH):
                    # 死亡判定
                    if Party[chara_num].alive is False:
                        Party[chara_num].way = None
                        Party[chara_num].target = None
                        continue
                    # 行動選択
                    Party[chara_num].way = self._myTurn(Party, chara_num)
                    # ターゲット選択
                    if Party[chara_num].way == 1: # 攻撃
                        Party[chara_num].target = self._partySelectTarget(Enemy, "攻撃", "倒した敵")
                    elif Party[chara_num].way == 2: # 防御
                        Party[chara_num].target = True
                    elif Party[chara_num].way == 3: # 魔法
                        Party[chara_num].my_magic = self._selectMagic(Party, chara_num)
                        if "ヒール" in Party[chara_num].magic[Party[chara_num].my_magic]:
                            Party[chara_num].target = self._partySelectTarget(Party, "ヒール", "倒れた味方")
                        else:
                            Party[chara_num].target = self._partySelectTarget(Enemy, "魔法攻撃", "倒した敵")
                    elif Party[chara_num].way == 4: # 属性変更
                        self._changeElement(Party, chara_num)
                        Party[chara_num].target = True
                    else: # 逃走
                        print("\n>>一行は逃げ出した")
                        time.sleep(TIME)
                        os.system('cls')
                        return

                # 敵のターン
                for chara_num in range(self.ENEMYLENGTH):
                    # 死亡判定
                    if Enemy[chara_num].alive is False:
                        Enemy[chara_num].way = None
                        Enemy[chara_num].target = None
                        continue
                    # 行動選択
                    if Enemy[chara_num].way_type == 0: # 攻撃
                        Enemy[chara_num].way = 1
                    elif Enemy[chara_num].way_type == 1: # 攻撃＆魔法
                        Enemy[chara_num].way = random.choice([1, 2], weights=[2, 1])
                    # ターゲット選択
                    Enemy[chara_num].target = self._enemySelectTarget(Party)
                
                print(PARTITION*2)

                # 攻撃処理
                party_counter = 0
                enemy_counter = 0
                # 防御表示
                self._showDefense(Party)
                time.sleep(TIME)
                for _ in range(max(self.PARTYLENGTH, self.ENEMYLENGTH)):
                    # 味方攻撃ループ
                    #try:
                    while(True):
                        # 死亡判定
                        if Party[party_counter].way == None or Party[party_counter].alive == False:
                            party_counter += 1
                            continue
                        # ターゲット死亡時敵ターゲット選択やり直し
                        if Enemy[Party[party_counter].target].alive is False:
                            Party[party_counter].target = random.randint(0, self.ENEMYLENGTH)
                            if Enemy[Party[party_counter].target].alive is False:
                                continue
                        # 各処理
                        if Party[party_counter].way == 1: # 物理攻撃
                            Party[party_counter].physicalAttack(Enemy[Party[party_counter].target], False)
                        elif Party[party_counter].way == 3: # 魔法攻撃
                            # 魔法レート設定
                            magic_rate = self._setMagicRate(Party, Enemy, party_counter)
                            # 魔法種類別処理
                            self._magicProcess(Party, Enemy, party_counter, magic_rate)
                        else: # 防御＆属性変化
                            party_counter += 1
                            continue
                        party_counter += 1
                        break
                    #except: pass
                    # 戦闘終了判定
                    self._endBattle(Party, Enemy)
                    time.sleep(TIME)
                    # 敵攻撃ループ
                    try:
                        while(True):
                            # 死亡判定
                            if Enemy[enemy_counter].way == None or Enemy[enemy_counter].alive == False:
                                enemy_counter += 1
                                continue
                            # ターゲット死亡時敵ターゲット選択やり直し
                            if Party[Enemy[enemy_counter].target].alive is False:
                                Enemy[enemy_counter].target = self._enemySelectTarget(Party)
                            # 各処理
                            if Enemy[enemy_counter].way == 1: # 物理攻撃
                                Enemy[enemy_counter].physicalAttack(Party[Enemy[enemy_counter].target], Party[Enemy[enemy_counter].target].target)
                            elif Enemy[enemy_counter].way == 2: # 魔法攻撃
                                Enemy[enemy_counter].magicalAttack(Party[Enemy[enemy_counter].target], Party[Enemy[enemy_counter].target].target, 1.0)
                            else: # 防御＆行動不能
                                enemy_counter += 1
                                continue
                            enemy_counter += 1
                            break
                    except: pass
                    # 戦闘終了判定
                    self._endBattle(Party, Enemy)
                    time.sleep(TIME)
                time.sleep(TIME*2)
                self.NOWTURN += 1
        except StopIteration: pass


    # 敵とエンカウント表示
    def _encountEnemy(self, Enemy) -> None:
        for chara_num in range(self.ENEMYLENGTH): print(f">>{Enemy[chara_num].charaName}が現れた!")
        time.sleep(TIME*2)
    
    # 敵味方のステータスを表示
    def _showStatuses(self, Party, Enemy) -> None:
        for x in range(self.PARTYLENGTH): Party[x].showStatus()
        for y in range(self.ENEMYLENGTH): Enemy[y].showStatus()
        time.sleep(TIME)

    # 行動選択
    def _myTurn(self, Party, counter) -> int:
        while(True):
            print(f"\n--{Party[counter].charaName}はどうする?--")
            time.sleep(TIME)
            print(f"1 : 攻撃\n2 : 防御\n3 : 魔法\n4 : 属性チェンジ\n5 : 逃げる")
            select = input("\n: ")
            try:
                select = int(select)
                if select >= 6 or select <= 0:
                    print("\n>>入力が間違っています。")
                    time.sleep(TIME)
                    continue
                break
            except ValueError:
                print("\n>>入力が間違っています。")
                time.sleep(TIME)
        return select

    # 魔法選択
    def _selectMagic(self, Party, chara_num) -> int:
        while(True):
            print(f"\n--どの魔法を使う?--")
            time.sleep(TIME)
            for counter in range(len(Party[chara_num].magic)):
                print(f">>{counter+1} : {Party[chara_num].magic[counter]}")
            select = input("\n: ")
            try:
                select = int(select)
                if select > len(Party[chara_num].magic) or select <= 0:
                    print("\n>>入力が間違っています。")
                    time.sleep(TIME)
                    continue
                break
            except ValueError:
                print("\n>>入力が間違っています。")
                time.sleep(TIME)
        return select-1

    # 属性変更
    def _changeElement(self, Party, chara_num) -> None:
        print(f"\n>>{Party[chara_num].charaName}は属性を変更した!")
        Party[chara_num].element = not Party[chara_num].element

    # 味方ターゲット選択
    def _partySelectTarget(self, Enemy, text_1, text_2) -> int:
        while(True):
            print(f"\n>>誰に{text_1}する? : ")
            for x in range(len(Enemy)):
                print(f"{x+1} : {Enemy[x].charaName}") #########################################
            select = input("\n: ")
            try:
                select = int(select)
                if select > self.ENEMYLENGTH or select <= 0:
                    print("\n>>入力が間違っています。")
                    time.sleep(TIME)
                    continue
                elif Enemy[select-1].hp <= 0:
                    print(f"\n>>{text_2}に攻撃はできません")
                    time.sleep(TIME)
                    continue
                break
            except ValueError:
                print("\n>>入力が間違っています。")
                time.sleep(TIME)
        return select - 1

    # 敵ターゲット選択
    def _enemySelectTarget(self, Party) -> int:
        while(True):
            select = random.randint(0, self.PARTYLENGTH-1)
            if Party[select].alive is False:
                continue
            else: break
        return select

    # 魔法レート設定
    def _setMagicRate(self, Party, Enemy, counter) -> float:
        if Party[counter].element == Enemy[Party[counter].target].element: magic_rate = 1.0
        else: magic_rate = 1.4
        return magic_rate

    # 魔法種類別処理
    def _magicProcess(self, Party, Enemy, counter, magic_rate) -> None:
        if MAGICNAME[1] == Party[counter].magic[Party[counter].my_magic]: # 初級ヒール
            Party[counter].heal(Party[Party[counter].target], 1.0)
        elif MAGICNAME[2] == Party[counter].magic[Party[counter].my_magic]: # 中級ヒール
            Party[counter].heal(Party[Party[counter].target], 1.5)
        elif MAGICNAME[3] == Party[counter].magic[Party[counter].my_magic]: # 上級ヒール
            Party[counter].heal(Party[Party[counter].target], 2.0)
        elif MAGICNAME[4] == Party[counter].magic[Party[counter].my_magic]:
            if Enemy[Party[counter].target].element is False: rate = 1.2
            else: rate = 0.6
            Party[counter].magicalAttack(Enemy[Party[counter].target], False, magic_rate * rate)
        # elif "" == Party[counter].magic[Party[counter].my_magic]:
        #     Party[counter].magicalAttack(Enemy[Party[counter].target], False, magic_rate)
        # elif "" == Party[counter].magic[Party[counter].my_magic]:
        #     Party[counter].magicalAttack(Enemy[Party[counter].target], False, magic_rate)
        # elif "" == Party[counter].magic[Party[counter].my_magic]:
        #     Party[counter].magicalAttack(Enemy[Party[counter].target], False, magic_rate)
        else: # 通常
            Party[counter].magicalAttack(Enemy[Party[counter].target], False, magic_rate)

    # 防御表示
    def _showDefense(self, Party) -> None:
        for chara_num in range(self.PARTYLENGTH):
            if Party[chara_num].way == 2:
                print(f"\n>>{Party[chara_num].charaName}は防御の姿勢をとった")

    # 戦闘終了
    def _endBattle(self, Party, Enemy) -> None:
        party_list = [0 for chara_num in range(self.PARTYLENGTH) if Party[chara_num].hp == 0]
        enemy_list = [0 for chara_num in range(self.ENEMYLENGTH) if Enemy[chara_num].hp == 0]
        if len(party_list) == self.PARTYLENGTH or len(enemy_list) == self.ENEMYLENGTH:
            print(PARTITION)
            time.sleep(TIME)
            print(f"\n>>戦闘終了")
            time.sleep(TIME)
            if len(party_list) == self.PARTYLENGTH: print(f"\n>>敗北")
            elif len(enemy_list) == self.ENEMYLENGTH: print(f"\n>>勝利!")
            time.sleep(TIME)
            _ = input("\n続けるには何かキーを入力:")
            raise StopIteration

# ステージ管理
class Stage(object):
    # ステージ表示
    def _showStage(self):
        print(">>名前        : 番号")
        print(PARTITION)
        if ONEONE is True: print(">>ステージ1-1 : 1")
        if ONETWO is True: print(">>ステージ1-2 : 2")      

    # ステージ選択 : 敵編成を返す
    def selectStage(self, Party) -> list[object]:
        while(True):
            # プレイ可能ステージ表示
            self._showStage()
            select = input("\n>>ステージを選択してください(Pキーで味方ステータス表示, cキーでゲーム終了) : ")
            # ステージ敵セット
            if select == "1" and ONEONE is True: Enemy = self._oneOne()
            elif select == "2" and ONETWO is True: Enemy = self._oneTwo()
            elif select == "p":
                os.system('cls')
                for x in range(len(Party)): Party[x].showStatus()
                while(True):
                    key = input("\n>>戻るにはPキーを押してください。 :")
                    if key == "p":
                        os.system('cls')
                        break
                    else:
                        print("\n>>入力が間違っています。")
                continue
            elif select == "c":
                print("\n>>ゲームを終了します")
                time.sleep(TIME*2)
                os.system('cls')
                sys.exit()
            else:
                print("\n>>入力が間違っています。")
                time.sleep(TIME)
                os.system('cls')
                continue
            break
        time.sleep(TIME)
        os.system('cls')
        return Enemy

    # ステージ1-1
    def _oneOne(self) -> list[object]:
        Enemy = []
        Enemy.append(EnemyClass("敵A", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, 0, False))
        return Enemy

    # ステージ1-2
    def _oneTwo(self) -> list[object]:
        Enemy = []
        Enemy.append(EnemyClass("敵A", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, 0, False))
        Enemy.append(EnemyClass("敵B", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, 0, False))
        return Enemy

if __name__ == "__main__":
    os.system('cls')
    # 味方編成
    Party = []
    Party.append(PartyClass("勇者", "Hero", 200, 10, 100, 30, 10, 10, 5, 50, True, True, ["通常", "初級ヒール"]))
    Party.append(PartyClass("剣士", "Fencer", 200, 0, 150, 30, 0, 10, 5, 50, True, True, ["通常"]))
    Party.append(PartyClass("魔法使い", "Wizard", 200, 50, 30, 30, 100, 5, 10, 50, True, True, ["通常", "中級ヒール", "光"]))
    Party.append(PartyClass("賢者", "Sage", 200, 50, 0, 30, 100, 5, 10, 50, True, True, ["通常", "上級ヒール", "光"]))
    # 本編開始
    while(True):
        World = Stage()
        # ステージ選択
        Enemy = World.selectStage(Party) 
        # 戦闘処理
        Battle(Party, Enemy)
        os.system('cls')