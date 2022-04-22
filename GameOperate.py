import secrets
from CharacterClass import *
import os, sys, time, random, config
import StreamTextModule as stm

CHARA_INFO = config.chara_info
MAGIC_NAME: list[str] = config.magic_name
TIME: float = 1.5
PARTITION: str = '-------------------------'

# 戦闘処理
class Battle(object):
    def __init__(self, Party, Enemy, World):
        self.PARTYLENGTH: int = len(Party) # 味方の人数
        self.ENEMYLENGTH: int = len(Enemy) # 敵の人数
        self.NOWTURN: int = 1 # 現在のターン

        stm.streamText(">>戦闘開始\n")
        # 敵とエンカウント表示
        self._encountEnemy(Enemy) 
        # メインループ開始
        try:
            while(True):
                # 表示リセット
                os.system('cls')
                # 現在のターン表示
                stm.streamText(f"\n>>現在のターン : {self.NOWTURN}\n")
                time.sleep(TIME)
                # 敵味方ステータス表示
                self._showStatuses(Party, Enemy)
                print(PARTITION*2)

                # 味方のターン
                for ch_num in range(self.PARTYLENGTH):
                    # 死亡判定
                    if Party[ch_num].alive is False:
                        Party[ch_num].way = None
                        Party[ch_num].target = None
                        continue
                    # 行動選択
                    Party[ch_num].way = self._myTurn(Party, ch_num)
                    # ターゲット選択
                    if Party[ch_num].way == 1: # 攻撃
                        Party[ch_num].target = self._partySelectTarget(Enemy, "攻撃", "倒した敵", self.ENEMYLENGTH)
                    elif Party[ch_num].way == 2: # 防御
                        Party[ch_num].target = None
                    elif Party[ch_num].way == 3: # 魔法
                        Party[ch_num].my_magic = self._selectMagic(Party, ch_num)
                        if "ヒール" in Party[ch_num].magic[Party[ch_num].my_magic]:
                            Party[ch_num].target = self._partySelectTarget(Party, "ヒール", "倒れた味方", self.PARTYLENGTH)
                        else:
                            Party[ch_num].target = self._partySelectTarget(Enemy, "魔法攻撃", "倒した敵", self.ENEMYLENGTH)
                    elif Party[ch_num].way == 4: # 属性変更
                        self._changeElement(Party, ch_num)
                        Party[ch_num].target = None
                    else: # 逃走
                        stm.streamText("\n>>一行は逃げ出した")
                        World.now_stage = 0
                        time.sleep(TIME)
                        os.system('cls')
                        return

                # 敵のターン
                for ch_num in range(self.ENEMYLENGTH):
                    # 死亡判定
                    if Enemy[ch_num].alive is False:
                        Enemy[ch_num].way = None
                        Enemy[ch_num].target = None
                        continue
                    # 行動選択
                    if Enemy[ch_num].way_type == 0: # 攻撃
                        Enemy[ch_num].way = 1
                    elif Enemy[ch_num].way_type == 1: # 攻撃＆魔法
                        Enemy[ch_num].way = random.choice([1, 2], weights=[2, 1])
                    # ターゲット選択
                    Enemy[ch_num].target = self._enemySelectTarget(Party)
                
                print(PARTITION*2)

                # 攻撃処理
                pt_ct: int = 0
                em_ct: int = 0
                # 防御表示
                self._showDefense(Party)
                time.sleep(TIME)
                for _ in range(max(self.PARTYLENGTH, self.ENEMYLENGTH)):
                    # 味方攻撃ループ
                    try:
                        while(True):
                            # 死亡判定
                            if Party[pt_ct].way == None or Party[pt_ct].alive == False or Party[pt_ct].target == None:
                                pt_ct += 1
                                continue
                            # ターゲット死亡時敵ターゲット選択やり直し
                            if Party[pt_ct].way == 3 and "ヒール" in Party[pt_ct].magic[Party[pt_ct].my_magic]:
                                if Party[Party[pt_ct].target].alive is False:
                                    # ヒールの場合
                                    Party[pt_ct].target = random.randint(0, self.PARTYLENGTH)
                                    if Party[Party[pt_ct].target].alive is False:
                                        continue
                            else:
                                if Enemy[Party[pt_ct].target].alive is False:
                                    Party[pt_ct].target = random.randint(0, self.ENEMYLENGTH)
                                    if Enemy[Party[pt_ct].target].alive is False:
                                        continue
                            # 各処理
                            if Party[pt_ct].way == 1: # 物理攻撃
                                Party[pt_ct].physicalAttack(Enemy[Party[pt_ct].target], Enemy[pt_ct].defence)
                            elif Party[pt_ct].way == 3: # 魔法攻撃
                                # 魔法レート設定
                                magic_rate = self._setMagicRate(Party, Enemy, pt_ct)
                                # 魔法種類別処理
                                self._magicProcess(Party, Enemy, pt_ct, magic_rate)
                            else: # 防御＆属性変化
                                pt_ct += 1
                                continue
                            pt_ct += 1
                            break
                    except: pass
                    # 戦闘終了判定
                    self._endBattle(Party, Enemy, World)
                    time.sleep(TIME)
                    # 敵攻撃ループ
                    try:
                        while(True):
                            # 死亡判定
                            if Enemy[em_ct].way == None or Enemy[em_ct].alive == False:
                                em_ct += 1
                                continue
                            # ターゲット死亡時敵ターゲット選択やり直し
                            if Party[Enemy[em_ct].target].alive is False:
                                Enemy[em_ct].target = self._enemySelectTarget(Party)
                            # 各処理
                            if Enemy[em_ct].way == 1: # 物理攻撃
                                Enemy[em_ct].physicalAttack(Party[Enemy[em_ct].target], Party[Enemy[em_ct].target].defence)
                            elif Enemy[em_ct].way == 2: # 魔法攻撃
                                Enemy[em_ct].magicalAttack(Party[Enemy[em_ct].target], Party[Enemy[em_ct].target].defence, 1.0)
                            else: # 防御＆行動不能
                                em_ct += 1
                                continue
                            em_ct += 1
                            break
                    except: pass
                    # 戦闘終了判定
                    self._endBattle(Party, Enemy, World)
                    time.sleep(TIME)
                time.sleep(TIME)
                self.NOWTURN += 1
                for num in range(self.PARTYLENGTH):
                    Party[num].defence = False
        except StopIteration: pass


    # 敵とエンカウント表示
    def _encountEnemy(self, Enemy):
        for ch_num in range(self.ENEMYLENGTH): print(f">>{Enemy[ch_num].charaName}が現れた!")
        time.sleep(TIME*2)
    
    # 敵味方のステータスを表示
    def _showStatuses(self, Party, Enemy):
        for x in range(self.PARTYLENGTH): Party[x].showStatus()
        for y in range(self.ENEMYLENGTH): Enemy[y].showStatus()
        time.sleep(TIME)

    # 行動選択
    def _myTurn(self, Party, counter):
        while(True):
            stm.streamText(f"\n--{Party[counter].charaName}はどうする?--")
            time.sleep(TIME)
            print(f"1 : 攻撃\n2 : 防御\n3 : 魔法\n4 : 属性チェンジ\n5 : 逃げる")
            select = input("\n: ")
            try:
                select = int(select)
                if select >= 6 or select <= 0:
                    stm.streamText("\n>>入力が間違っています。")
                    time.sleep(TIME)
                    continue
                break
            except ValueError:
                stm.streamText("\n>>入力が間違っています。")
                time.sleep(TIME)
        return select

    # 魔法選択
    def _selectMagic(self, Party, ch_num):
        while(True):
            stm.streamText("\n--どの魔法を使う?--")
            time.sleep(TIME)
            for counter in range(len(Party[ch_num].magic)):
                print(f">>{counter+1} : {Party[ch_num].magic[counter]}")
            select = input("\n: ")
            try:
                select = int(select)
                if select > len(Party[ch_num].magic) or select <= 0:
                    stm.streamText("\n>>入力が間違っています。")
                    time.sleep(TIME)
                    continue
                break
            except ValueError:
                stm.streamText("\n>>入力が間違っています。")
                time.sleep(TIME)
        return select-1

    # 属性変更
    def _changeElement(self, Party, ch_num):
        stm.streamText(f"\n>>{Party[ch_num].charaName}は属性を変更した!")
        Party[ch_num].element = not Party[ch_num].element

    # 味方ターゲット選択
    def _partySelectTarget(self, Enemy, text_1, text_2, length):
        while(True):
            stm.streamText(f"\n>>誰に{text_1}する? : ")
            for x in range(length):
                print(f"{x+1} : {Enemy[x].charaName}")
            select = input("\n: ")
            try:
                select = int(select)
                if select > length or select <= 0:
                    stm.streamText("\n>>入力が間違っています。")
                    time.sleep(TIME)
                    continue
                elif Enemy[select-1].hp <= 0:
                    stm.streamText(f"\n>>{text_2}に攻撃はできません")
                    time.sleep(TIME)
                    continue
                break
            except ValueError:
                stm.streamText("\n>>入力が間違っています。")
                time.sleep(TIME)
        return select - 1

    # 敵ターゲット選択
    def _enemySelectTarget(self, Party):
        while(True):
            select = random.randint(0, self.PARTYLENGTH-1)
            if Party[select].alive is False:
                continue
            else: break
        return select

    # 魔法レート設定
    def _setMagicRate(self, Party, Enemy, counter):
        # ヒールの場合例外
        if "ヒール" in Party[counter].magic[Party[counter].my_magic]:
            magic_rate = 1.4
        else:
            if Party[counter].element == Enemy[Party[counter].target].element: magic_rate = 1.0
            else: magic_rate = 1.4
        return magic_rate

    # 魔法種類別処理
    def _magicProcess(self, Party, Enemy, counter, magic_rate):
        if MAGIC_NAME[1] == Party[counter].magic[Party[counter].my_magic]: # 初級ヒール
            Party[counter].heal(Party[Party[counter].target], 1.0)
        elif MAGIC_NAME[2] == Party[counter].magic[Party[counter].my_magic]: # 中級ヒール
            Party[counter].heal(Party[Party[counter].target], 1.5)
        elif MAGIC_NAME[3] == Party[counter].magic[Party[counter].my_magic]: # 上級ヒール
            Party[counter].heal(Party[Party[counter].target], 2.0)
        elif MAGIC_NAME[4] == Party[counter].magic[Party[counter].my_magic]: # 光
            if Enemy[Party[counter].target].element is False: rate = 1.3
            else: rate = 0.2
            Party[counter].magicalAttack(Enemy[Party[counter].target], Enemy[counter].defence, magic_rate * rate)
        elif MAGIC_NAME[5] == Party[counter].magic[Party[counter].my_magic]:# 闇
            if Enemy[Party[counter].target].element is True: rate = 1.3
            else: rate = 0.2
            Party[counter].magicalAttack(Enemy[Party[counter].target], Enemy[counter].defence, magic_rate * rate)
        else: # 通常
            Party[counter].magicalAttack(Enemy[Party[counter].target], Enemy[counter].defence, magic_rate)

    # 防御表示
    def _showDefense(self, Party):
        for ch_num in range(self.PARTYLENGTH):
            if Party[ch_num].way == 2:
                stm.streamText(f"\n>>{Party[ch_num].charaName}は防御の姿勢をとった")
                Party[ch_num].defence = True

    # 戦闘終了
    def _endBattle(self, Party, Enemy, World):
        party_list: list[int] = [0 for ch_num in range(self.PARTYLENGTH) if Party[ch_num].hp == 0]
        enemy_list: list[int] = [0 for ch_num in range(self.ENEMYLENGTH) if Enemy[ch_num].hp == 0]
        if len(party_list) == self.PARTYLENGTH or len(enemy_list) == self.ENEMYLENGTH:
            time.sleep(TIME)
            os.system('cls')
            stm.streamText("\n>>戦闘終了")
            time.sleep(TIME)
            if len(party_list) == self.PARTYLENGTH: print(f"\n>>敗北")
            elif len(enemy_list) == self.ENEMYLENGTH: print(f"\n>>勝利!")
            time.sleep(TIME)
            stm.streamText(f'\nそれぞれが{World.exp}exp手に入れた')
            time.sleep(TIME)
            for num in range(self.PARTYLENGTH):
                Party[num].add_exp(World)
            stm.streamText(f'\n{World.skill_point}のスキルポイントを手に入れた')
            World.all_skill_point += World.skill_point
            if World.new_chara != None:
                os.system('cls')
                stm.streamText(f'新しいキャラクターが仲間になりました: {CHARA_INFO[World.new_chara][0]} level 1')
                stm.streamText('編成画面からパーティーに加えれます')
                World.new_chara = None
            _ = input("\n続けるには何かキーを入力:")
            raise StopIteration

# ステージ管理
class Stage(object):
    def __init__(self):
        self.stage_num: list[bool] = [True, False]
        self.new_chara: int = None
        self._all_skill_point: int = 0

    # ステージ表示
    def _showStage(self):
        print(">>名前      : 番号")
        print(PARTITION)
        for num in range(len(self.stage_num)):
            if self.stage_num[num] == True:
                print(f">>ステージ{num+1} : {num+1}") 

    # ステージ選択 : 敵編成を返す
    def selectStage(self, Party):
        while(True):
            # プレイ可能ステージ表示
            self._showStage()
            select = input("\n>>ステージを選択してください(Pキーで味方ステータス表示, cキーでゲーム終了) : ")
            # ステージ敵セット
            if select == "1" and self.stage_num[0] is True: Enemy = self._oneOne()
            elif select == "2" and self.stage_num[1] is True: Enemy = self._oneTwo()
            # ステータス表示画面
            elif select.lower() == "p":
                # メニュー表示
                self._menu_show(Party)
                continue
            # ゲーム終了
            elif select.lower() == "c": self._end_game()
            else:
                stm.streamText("\n>>入力が間違っています。")
                time.sleep(TIME)
                os.system('cls')
                continue
            break
        time.sleep(TIME)
        os.system('cls')
        return Enemy

    # メニュー画面
    def _menu_show(self, Party):
        os.system('cls')
        # ステータス表示
        for x in range(len(Party)): Party[x].showStatus()
        while(True):
            stm.streamText('--メニュー--')
            print("1: スキルポイント振り分け\np: もどる")
            key = input(": ")
            if key == '1': self._skill_point_show(Party)
            elif key.lower() == "p":
                os.system('cls')
                break
            else:
                stm.streamText("\n>>入力が間違っています。")

    # スキルポイント振り分け画面
    def _skill_point_show(self, Party):
        while(True):
            os.system('cls')
            stm.streamText(f'>>現在のスキルポイントは{self._all_skill_point}です')
            stm.streamText('\n>>誰に振り分ける?')
            for num in range(len(Party)):
                print(f'{num+1}: {Party[num].charaName}')
            select = input(': ')
            if int(select) <= len(Party) or int(select) > 0: break
            stm.streamText('>>入力が間違っています')
        self._point_assign(int(select), Party)
        os.system('cls')

    def _point_assign(self, select, Party):
        while(True):
            os.system('cls')
            stm.streamText('>>どのステータスに振り分ける?')
            print('''1: HP
2: MP
3: STR
4: VTL
5: Mana
6: AATK
7: AMana
8: Speed''')
            status_select = input(": ")
            if int(status_select) < 9 or int(status_select) > 0: break
            stm.streamText('>>入力が間違っています')
        while(True):
            os.sysem('cls')
            stm.streamText('>>どれだけ振り分ける?')
            num = input(": ")
            if num <= self._all_skill_point: break
            stm.streamText('>>入力値が多きすぎます')
        Party[select].point_assign(int(status_select), int(num)
        stm.streamText('>>振り分け完了')
 
    # ゲーム終了
    def _end_game(self):
        stm.streamText("\n>>ゲームを終了します")
        time.sleep(TIME*2)
        os.system('cls')
        sys.exit()

    # ステージ1-1
    def _oneOne(self):
        Enemy = []
        Enemy.append(EnemyClass("敵A", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, 0, False))
        self.now_stage = 1
        self.exp = 100
        self.skill_point = 10
        return Enemy

    # ステージ1-2
    def _oneTwo(self):
        Enemy = []
        Enemy.append(EnemyClass("敵A", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, 0, False))
        Enemy.append(EnemyClass("敵B", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, 0, False))
        self.now_stage = 2
        self.exp = 300
        self.skill_point = 20
        return Enemy

    # ステージ1-3
    def _oneThree(self):
        Enemy = []
        Enemy.append(EnemyClass("敵A", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, 0, False))
        Enemy.append(EnemyClass("敵B", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, 0, False))
        Enemy.append(EnemyClass("敵C", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, 0, False))
        Enemy.append(EnemyClass("敵D", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, 0, False))
        self.now_stage = 3
        self.exp = 500
        self.skill_point = 40
        return Enemy

# ゲーム説明
def game_explain():
    print(PARTITION*2)
    print('''これはCUIで遊べるRPGゲームのようなものです。
実装状況: ステージ3まで
==属性について==
このゲームには光と闇の二属性があり(増える予定あり)
"光"と"闇"という名前の魔法も実装されています。
自分と同じ属性の相手に魔法を使うとあまり効果がありませんが、
違う属性の相手に魔法を使うとダメージが加算されます。
例) 自分(攻撃): 光　相手: 光　→　ダメージ↓
    自分(攻撃): 光　相手: 闇　→　ダメージ↑
属性チェンジをすると自分の属性を変えられるので属性を変えて大ダメージを狙うこともできます。
また敵はこの属性攻撃をしてきません。
''')    
    print(PARTITION*2)
    _ = input(">>続けるには何かキーを入力してください: ")

# ほんへ
if __name__ == "__main__":
    # ゲーム説明
    while(True):
        os.system('cls')
        select = input('>>ゲーム説明を見ますか?[y/n]: ')
        if select.lower() == 'y':
            game_explain()
            break
        elif select.lower() == 'n': break
        else:
            print('>>入力が間違っています')
            time.sleep(TIME)
    # 初期味方編成
    Party = []
    Party.append(PartyClass(*CHARA_INFO[0]))
    Party.append(PartyClass(*CHARA_INFO[1]))
    Party.append(PartyClass(*CHARA_INFO[2]))
    Party.append(PartyClass(*CHARA_INFO[3]))
    World = Stage()
    # 本編開始
    while(True):
        os.system('cls')
        # ステージ選択
        Enemy = World.selectStage(Party)
        # 戦闘処理
        Battle(Party, Enemy, World)
        # 次ステージ開放
        # try:
        World.stage_num[World.now_stage] = True
        World.stage_num.append(False)
        # except: pass
