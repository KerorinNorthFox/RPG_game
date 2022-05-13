import StreamTextModule as stm
from Character import *
import Database, Battle
import os, sys, time, random, config

CHARA_INFO = config.chara_info
MAGIC_NAME: list[str] = config.magic_name

# ステージ管理
class Stage(object): # DONE
    def __init__(self):
        self.func_list = [self._oneOne(), self._oneTwo(), self._oneThree()]
        self.stage_num: list[bool] = [True, False]
        self._all_skill_point: int = 0
        self.save: bool = False

    # ステージ表示
    def _showStage(self):
        os.system('cls')
        print(">>名前      : 番号")
        print(PARTITION)
        for i, num in enumerate(self.stage_num):
            if num == True: print(f">>ステージ{i+1} : {i+1}") 

    # ステージ選択 : 敵編成を返す
    def selectStage(self, Party, Me):
        while(True):
            # プレイ可能ステージ表示
            self._showStage()
            key = input("\n>>ステージを選択してください(Pキーで味方ステータス表示, sキーでセーブ ,cキーでゲーム終了) : ")
            try:
                key = int(key)
                # ステージ選択
                Enemy = None
                for i, num in enumerate(self.stage_num):
                    if key == i+1 and num is True:
                        # ステージ敵セット
                        Enemy = self.func_list[i]
                        break
                if Enemy is None:
                    stm.streamText("\n>>入力が間違っています。")
                    continue
                else: break
                    
            except:
                # 条件分岐
                if key.lower() == 'p':
                    # メニュー表示
                    self._menuShow(Party)
                    continue
                # セーブ
                elif key.lower() == 's':
                    if Me.login_status is True: self._saveProgress(Me, Party)
                    else: stm.streamText(">>ゲストでログイン中です。セーブできません")
                    time.sleep(TIME)
                    os.system('cls')
                    continue

                # ################
                # elif key.lower() == 'r':
                #     Party[0].hp = 0
                #     os.system('cls')
                #     continue
                # ###############
                        
                # ゲーム終了
                elif key.lower() == 'c': self._endGame(Me, Party)
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
    def _menuShow(self, Party):
        os.system('cls')
        # ステータス表示
        for num in Party: num.showStatus()
        while(True):
            stm.streamText('--メニュー--')
            print("1: スキルポイント振り分け(ベータ版)\np: もどる")
            key = input(": ")
            if key == '1': self._skillPointShow(Party)
            elif key.lower() == "p":
                os.system('cls')
                break
            else:
                stm.streamText("\n>>入力が間違っています。")

    # スキルポイント振り分け画面
    def _skillPointShow(self, Party):
        while(True):
            os.system('cls')
            stm.streamText(f'>>現在のスキルポイントは{self._all_skill_point}です\n>>誰に振り分ける?')
            for i, num in enumerate(Party):
                print(f'{i+1}: {num.name}')
            key = input(': ')
            if int(key) < len(Party) or int(key) > 0: break
            stm.streamText('>>入力が間違っています')
        self._pointAssign(int(key), Party)
        os.system('cls')

    def _pointAssign(self, key, Party):
        # 選択
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
        # 振り分け量入力
        while(True):
            os.system('cls')
            stm.streamText('>>どれだけ振り分ける?(現在のスキルポイント: {self._all_skill_point})')
            num = input(": ")
            if int(num) <= self._all_skill_point: break
            stm.streamText('>>入力値が多きすぎます')
        Party[key].point_assign(int(status_select), int(num))
        stm.streamText('>>振り分け完了')

    # セーブ
    def _saveProgress(self, Me, Party):
        Me.saveObj(Party, self)
        stm.streamText("\n>>セーブ完了")
        time.sleep(TIME)

    # ゲーム終了
    def _endGame(self, Me, Party):
        if self.save is False:
            stm.streamText(">>進行状況がセーブされていません!")
            key = input(">>セーブしますか?[y/n] :")
            if key.lower() == 'y': self._saveProgress(Me, Party)
        stm.streamText("\n>>ゲームを終了します")
        time.sleep(TIME*2)
        os.system('cls')
        sys.exit()

    # ステージ1-1
    def _oneOne(self):
        Enemy = []
        Enemy.append(EnemyClass("敵A", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, False, 0))
        self.now_stage = 1
        self.exp = 100
        self.skill_point = 10
        return Enemy

    # ステージ1-2
    def _oneTwo(self):
        Enemy = []
        Enemy.append(EnemyClass("敵A", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, False, 0))
        Enemy.append(EnemyClass("敵B", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, False, 0))
        self.now_stage = 2
        self.exp = 300
        self.skill_point = 20
        return Enemy

    # ステージ1-3
    def _oneThree(self):
        Enemy = []
        Enemy.append(EnemyClass("敵A", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, False, 0))
        Enemy.append(EnemyClass("敵B", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, True, 0))
        Enemy.append(EnemyClass("敵C", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, False, 0))
        Enemy.append(EnemyClass("敵D", "Zombie", 200, 0, 100, 30, 0, 0, 0, 50, True, True, 0))
        self.now_stage = 3
        self.exp = 500
        self.skill_point = 40
        return Enemy

# ゲーム説明本文
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
    # ログイン処理
    Me = Database.Database()
    # ゲスト、最初時
    if Me.login_status is False or Me.first is True:
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

        # 世界生成
        World = Stage()

        if Me.login_status is False: World.save = None

    # セーブデータ読み込み
    else: Party, World = Me.setObj()

    #本編開始
    while(True):
        # ステージ選択
        Enemy = World.selectStage(Party, Me)
        # 戦闘処理
        # Battle(Party, Enemy, World)
        # 次ステージ開放
        World.stage_num[World.now_stage] = True
        World.stage_num.append(False)
        