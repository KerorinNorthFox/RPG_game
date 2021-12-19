from CharacterClass import *
import os, sys, time

PARTITION = '-------------------------'
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
        while(True):
            party_target_list = [] # 0~
            enemy_target_list = [] # 0~
            party_select_way = [] # 1~
            enemy_select_way = [] # 1~

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
                    party_target_list.append(None)
                    party_select_way.append(None)
                    continue
                # 行動選択
                party_select_way.append(self._myTurn(Party, chara_num))
                # ターゲット選択
                if party_select_way[chara_num] == 1 or party_select_way[chara_num] == 3: # 攻撃＆魔法
                    party_target_list = self._partySelectTarget(Enemy, party_target_list, "攻撃")
                elif party_select_way[chara_num] == 2: # 防御
                    party_target_list.append(True)
                else: # 逃走
                    print("\n>>一行は逃げ出した")
                    time.sleep(2)
                    os.system('cls')
                    return

            # 敵のターン
            for chara_num in range(self.ENEMYLENGTH):
                # 死亡判定
                if Enemy[chara_num].alive is False:
                    enemy_target_list.append(None)
                    enemy_select_way.append(None)
                    continue
                # 行動選択
                if Enemy[chara_num].way_type == 0: # 攻撃
                    enemy_select_way.append(1)
                elif Enemy[chara_num].way_type == 1: # 攻撃＆魔法
                    enemy_select_way.append(random.choice([1, 2], weights=[2, 1]))
                # ターゲット選択
                enemy_target_list = self._enemySelectTarget(Party, enemy_target_list)
            
            time.sleep(2)
            # 攻撃処理
            for num in range(max(self.PARTYLENGTH, self.ENEMYLENGTH)):
                print(f">>>>>>>>{num}")
                try:
                    # 味方ターン
                    if party_select_way[num] == 1: Party[num].physicalAttack(Enemy[party_target_list[num]], False) # 物理攻撃
                    elif party_select_way[num] == 2: print(f"\n>>{Party[num].charaName}は防御の姿勢をとった") # 防御
                    elif party_select_way[num] == 3: Party[num].magicalAttack(Enemy[party_target_list[num]], False) # 魔法攻撃
                except: pass
                time.sleep(2)
                try:
                    # 敵ターン
                    if enemy_select_way[num] == 1: Enemy[num].physicalAttack(Party[enemy_target_list[num]], party_select_way[num]) # 物理攻撃
                    elif enemy_select_way[num] == 2: Enemy[num].magicalAttack(Party[enemy_target_list[num]], party_select_way[num]) # 魔法攻撃
                except: pass
                time.sleep(2)
                

            print(party_select_way)
            print(party_target_list)
            print(enemy_select_way)
            print(enemy_target_list)
            a = input()


    # 敵とエンカウント表示
    def _encountEnemy(self, Enemy):
        for chara_num in range(self.ENEMYLENGTH): print(f">>{Enemy[chara_num].charaName}が現れた!")
        time.sleep(4)
    
    # 敵味方のステータスを表示
    def _showStatuses(self, Party, Enemy):
        for x in range(self.PARTYLENGTH): Party[x].showStatus()
        for y in range(self.ENEMYLENGTH): Enemy[y].showStatus()
        time.sleep(2)

    # 行動選択
    def _myTurn(self, Party, counter) -> int:
        while(True):
            print(f"\n--{Party[counter].charaName}はどうする?--")
            time.sleep(2)
            print(f"1 : 攻撃\n2 : 防御\n3 : 魔法\n4 : 逃げる")
            select = input("\n: ")
            try:
                select = int(select)
                if select >= 5 or select <= 0:
                    print("\n>>入力が間違っています。")
                    time.sleep(2)
                    continue
                break
            except ValueError:
                print("\n>>入力が間違っています。")
                time.sleep(2)
        return select

    # 味方ターゲット選択
    def _partySelectTarget(self, Enemy, party_target_list, text) -> list[int]:
        while(True):
            print(f"\n>>誰に{text}する? : ")
            for x in range(self.ENEMYLENGTH):
                print(f"{x+1} : {Enemy[x].charaName}") #########################################
            select = input("\n: ")
            try:
                select = int(select)
                if select > self.ENEMYLENGTH or select <= 0:
                    print("\n>>入力が間違っています。")
                    time.sleep(2)
                    continue
                elif Enemy[select-1].alive is False:
                    print("\n>>倒した敵に攻撃はできません")
                    time.sleep(2)
                    continue
                break
            except ValueError:
                print("\n>>入力が間違っています。")
                time.sleep(2)
        # リストにターゲット追加
        party_target_list.append(select-1)
        return party_target_list

    # 敵ターゲット選択
    def _enemySelectTarget(self, Party, enemy_target_list) -> list[int]:
        while(True):
            select = random.randint(0, self.PARTYLENGTH-1)
            if Party[select].alive is False:
                continue
            else: break
        # リストにターゲット追加
        enemy_target_list.append(select)
        return enemy_target_list

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
                time.sleep(4)
                os.system('cls')
                sys.exit()
            else:
                print("\n>>入力が間違っています。")
                time.sleep(2)
                os.system('cls')
                continue
            break
        time.sleep(2)
        os.system('cls')
        return Enemy

    # ステージ1-1
    def _oneOne(self) -> list[object]:
        Enemy = []
        Enemy.append(EnemyClass("敵A", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, 0))
        return Enemy

    # ステージ1-2
    def _oneTwo(self) -> list[object]:
        Enemy = []
        Enemy.append(EnemyClass("敵A", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, 0))
        Enemy.append(EnemyClass("敵B", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, 0))
        return Enemy


if __name__ == "__main__":
    os.system('cls')
    # 味方編成
    Party = []
    Party.append(PartyClass("勇者", "Hero", 200, 10, 100, 30, 10, 10, 5, 50, True))
    Party.append(PartyClass("剣士", "Fencer", 200, 0, 150, 30, 0, 10, 5, 50, False))
    Party.append(PartyClass("魔法使い", "Wizard", 200, 50, 30, 30, 100, 5, 10, 50, True))
    Party.append(PartyClass("賢者", "Sage", 200, 50, 0, 30, 100, 5, 10, 50, True))
    # 本編開始
    while(True):
        World = Stage()
        # ステージ選択
        Enemy = World.selectStage(Party) 
        # 戦闘処理
        Battle(Party, Enemy)
    