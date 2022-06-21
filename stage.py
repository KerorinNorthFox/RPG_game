import os
import time
import random

import config
import streamtextmodule as stm
import database
from character import *


CHARA_INFO: list[str | int] = config.chara_info
MAGIC_NAME: list[str] = config.magic_name


# 戦闘処理
class Battle(object):
    def __init__(self, Party:list[object], Enemy:list[object], World:object) -> None:
        self.PARTYLENGTH: int = len(Party) # 味方の人数
        self.ENEMYLENGTH: int = len(Enemy) # 敵の人数
        now_turn: int = 1 # 現在のターン

        stm.stream_text("\n>>戦闘開始")
        # 敵とエンカウント表示
        self._encount_enemy(Enemy) 

        # メインループ開始
        try:
            while(True):
                # 表示リセット
                os.system(CLEAR)
                # 現在のターン表示
                stm.stream_text(f"\n>>現在のターン: {now_turn}\n")
                time.sleep(TIME)
                # 敵味方ステータス表示
                self._show_statuses(Party, Enemy)
                print(PARTITION*2)

                # 味方のターン
                for chara in Party:
                    # 死亡判定
                    if chara.alive is False:
                        chara.way = None
                        chara.target = None
                        continue
                    # 行動選択
                    chara.way = self._my_turn(chara.name)
                    # ターゲット選択
                    if chara.way == 1: # 攻撃
                        chara.target = self._party_select_target(Enemy, "攻撃", "倒した敵", self.ENEMYLENGTH)
                    elif chara.way == 2: # 防御
                        chara.target = None
                    elif chara.way == 3: # 魔法
                        chara.selected_magic = self._select_magic(chara.magic)
                        if "ヒール" in chara.magic[chara.selected_magic]:
                            chara.target = self._party_select_target(Party, "ヒール", "倒れた味方", self.PARTYLENGTH)
                        else:
                            chara.target = self._party_select_target(Enemy, "魔法攻撃", "倒した敵", self.ENEMYLENGTH)
                    elif chara.way == 4: # 属性変更
                        self._change_element(chara)
                        chara.target = None
                    else: # 逃走
                        stm.stream_text("\n>>一行は逃げ出した")
                        World.now_stage = 0
                        time.sleep(TIME)
                        os.system(CLEAR)
                        return

                # 敵のターン
                for chara in Enemy:
                    # 死亡判定
                    if chara.alive is False:
                        chara.way = None
                        chara.target = None
                        continue
                    # 行動選択
                    if chara.way_type == 0: # 攻撃
                        chara.way = 1
                    elif chara.way_type == 1: # 攻撃＆魔法
                        chara.way = random.choice([1, 2], weights=[2, 1])
                    # ターゲット選択
                    chara.target = self._enemy_select_target(Party)

                print(PARTITION*2)

                # 攻撃処理
                pt_ct: int = 0
                em_ct: int = 0
                # 防御表示
                self._show_defense(Party)
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
                            if Party[pt_ct].way == 3 and "ヒール" in Party[pt_ct].magic[Party[pt_ct].selected_magic]:
                                if not Party[Party[pt_ct].target].alive:
                                    # ヒールの場合
                                    Party[pt_ct].target = random.randint(0, self.PARTYLENGTH)
                                    if not Party[Party[pt_ct].target].alive:
                                        continue
                            else:
                                if not Enemy[Party[pt_ct].target].alive:
                                    Party[pt_ct].target = random.randint(0, self.ENEMYLENGTH)
                                    if not Enemy[Party[pt_ct].target].alive:
                                        continue
                            
                            # 各処理
                            if Party[pt_ct].way == 1: # 物理攻撃
                                Party[pt_ct].physical_attack(Enemy[Party[pt_ct].target], False)
                            elif Party[pt_ct].way == 3: # 魔法攻撃
                                # 魔法レート設定
                                magic_rate = self._set_magic_rate(Party[pt_ct], Enemy)
                                # 魔法種類別処理
                                self._magic_process(Party, Enemy, pt_ct, magic_rate)
                            else: # 防御＆属性変化
                                pt_ct += 1
                                continue
                            pt_ct += 1
                            break
                    except:
                        pass
                    # 戦闘終了判定
                    self._end_battle(Party, Enemy, World)
                    time.sleep(TIME)
                    # 敵攻撃ループ
                    try:
                        while(True):
                            # 死亡判定
                            if Enemy[em_ct].way == None or Enemy[em_ct].alive == False:
                                em_ct += 1
                                continue
                            # ターゲット死亡時敵ターゲット選択やり直し
                            if not Party[Enemy[em_ct].target].alive:
                                Enemy[em_ct].target = self._enemy_select_target(Party)
                            # 各処理
                            if Enemy[em_ct].way == 1: # 物理攻撃
                                Enemy[em_ct].physical_attack(Party[Enemy[em_ct].target], Party[Enemy[em_ct].target].defence)
                            elif Enemy[em_ct].way == 2: # 魔法攻撃
                                Enemy[em_ct].magical_attack(Party[Enemy[em_ct].target], Party[Enemy[em_ct].target].defence, 1.0)
                            else: # 防御＆行動不能
                                em_ct += 1
                                continue
                            em_ct += 1
                            break
                    except:
                        pass
                    # 戦闘終了判定
                    self._end_battle(Party, Enemy, World)
                    time.sleep(TIME)
                time.sleep(TIME)
                now_turn += 1
                for chara in Party:
                    chara.defence = False
        except StopIteration:
            pass

        
    # 敵とエンカウント表示
    def _encount_enemy(self, Enemy:list[object]) -> None:
        for num in Enemy:
            print(f">>{num.name}が現れた!")
        time.sleep(TIME*2)

    # 敵味方のステータスを表示
    def _show_statuses(self, Party:list[object], Enemy:list[object]) -> None:
        for x in Party:
            x.show_status()
        for y in Enemy:
            y.show_status()
        time.sleep(TIME)

    # 行動選択
    def _my_turn(self, name:str) -> int:
        while(True):
            stm.stream_text(f"\n--{name}はどうする?--")
            time.sleep(TIME/2)
            print(f"1: 攻撃\n2: 防御\n3: 魔法\n4: 属性チェンジ\n5: 逃げる")
            select: str = input("\n: ")
            try:
                select: int = int(select)
                if select >= 6 or select <= 0:
                    stm.stream_text("\n>>入力が間違っています。")
                    time.sleep(TIME)
                    continue
                break
            except ValueError:
                stm.stream_text("\n>>入力が間違っています。")
                time.sleep(TIME)
        return select

    # 魔法選択
    def _select_magic(self, magic:list[str]) -> int:
        while(True):
            stm.stream_text("\n--どの魔法を使う?--")
            time.sleep(TIME)
            for i, num in enumerate(magic):
                print(f">>{i+1} : {num}")
            select: str = input("\n: ")
            try:
                select: int = int(select)
                if select > len(magic) or select <= 0:
                    stm.stream_text("\n>>入力が間違っています。")
                    time.sleep(TIME)
                    continue
                break
            except ValueError:
                stm.stream_text("\n>>入力が間違っています。")
                time.sleep(TIME)
        return select-1

    # 属性変更
    def _change_element(self, chara:object) -> None:
        stm.stream_text(f"\n>>{chara.name}は属性を変更した!")
        chara.element = not chara.element

    # 味方ターゲット選択
    def _party_select_target(self, Enemy:list[object], text_1:str, text_2:str, length:int) -> int:
        while(True):
            stm.stream_text(f"\n>>誰に{text_1}する?")
            for i, chara in enumerate(Enemy):
                print(f"{i+1}: {chara.name}")
            select: str = input("\n: ")
            try:
                select: int = int(select)
                if select > length or select <= 0:
                    stm.stream_text("\n>>入力が間違っています。")
                    time.sleep(TIME)
                    continue
                elif Enemy[select-1].hp <= 0:
                    stm.stream_text(f"\n>>{text_2}に{text_1}はできません")
                    time.sleep(TIME)
                    continue
                break
            except ValueError:
                stm.stream_text("\n>>入力が間違っています。")
                time.sleep(TIME)
        return select-1

    # 敵ターゲット選択
    def _enemy_select_target(self, Party:list[object]) -> int:
        while(True):
            select: int = random.randint(0, self.PARTYLENGTH-1)
            if not Party[select].alive:
                continue
            else:
                break
        return select

    # 魔法レート設定
    def _set_magic_rate(self, chara:object, Enemy:object) -> float:
        # ヒールの場合例外
        if "ヒール" in chara.magic[chara.selected_magic]:
            magic_rate: float = 1.4
        else:
            if chara.element == Enemy[chara.target].element:
                magic_rate: float = 1.0
            else:
                magic_rate: float = 1.4
        return magic_rate

    # 魔法種類別処理
    def _magic_process(self, Party:list[object], Enemy:list[object], i:int, magic_rate:float) -> None:
        if MAGIC_NAME[1] == Party[i].magic[Party[i].selected_magic]: # 初級ヒール
            Party[i].heal(Party[Party[i].target], 1.0)
        elif MAGIC_NAME[2] == Party[i].magic[Party[i].selected_magic]: # 中級ヒール
            Party[i].heal(Party[Party[i].target], 1.5)
        elif MAGIC_NAME[3] == Party[i].magic[Party[i].selected_magic]: # 上級ヒール
            Party[i].heal(Party[Party[i].target], 2.0)
        elif MAGIC_NAME[4] == Party[i].magic[Party[i].selected_magic]: # 光
            if not Enemy[Party[i].target].element:
                rate: float = 1.3
            else:
                rate: float = 0.2
            Party[i].magical_attack(Enemy[Party[i].target], False, magic_rate * rate)
        # elif MAGIC_NAME[5] == Party[i].magic[Party[i].selected_magic]:# 闇
        #     if Enemy[Party[i].target].element:
        #         rate: float = 1.3
        #     else:
        #         rate: float = 0.2
        #     Party[i].magical_attack(Enemy[Party[i].target], False, magic_rate * rate)
        else: # 通常
            Party[i].magical_attack(Enemy[Party[i].target], False, magic_rate)

    # 防御表示
    def _show_defense(self, Party:list[object]) -> None:
        for chara in Party:
            if chara.way == 2:
                stm.stream_text(f">>{chara.name}は防御の姿勢をとった")
                chara.defence = True

    # 戦闘終了
    def _end_battle(self, Party:list[object], Enemy:list[object], World:object) -> None:
        World.save = False
        killed_party_len: int = len([0 for chara in Party if chara.hp == 0])
        killed_enemy_len: int = len([0 for chara in Enemy if chara.hp == 0])

        # 終了判定
        if killed_party_len == self.PARTYLENGTH or killed_enemy_len == self.ENEMYLENGTH:
            time.sleep(TIME)
            os.system(CLEAR)
            stm.stream_text("\n>>戦闘終了")
            time.sleep(TIME)

            if killed_party_len < killed_enemy_len:
                print(f"\n>>勝利!")
                exp_level: str = 'victory'
            elif killed_party_len > killed_enemy_len:
                print(f"\n>>敗北")
                exp_level: str = 'defeat'
            else:
                print("\n>>引き分け")
                exp_level: str = 'draw'
            time.sleep(TIME)

            if exp_level == 'victory':
                exp: int = World.exp
            elif exp_level == 'defeat':
                exp: int = World.exp / 5
            elif exp_level == 'draw':
                exp: int = World.exp / 2

            # 経験値加算
            stm.stream_text(f'\nそれぞれが{exp}exp手に入れた')
            time.sleep(TIME)
            for chara in Party:
                chara.add_exp(exp)

            # スキルポイント加算
            stm.stream_text(f'\n{World.skill_point}のスキルポイントを手に入れた')
            World.all_skill_point += World.skill_point
            # #新キャラ
            # if World.new_chara != None:
            #     os.system('cls')
            #     stm.streamText(f'新しいキャラクターが仲間になりました: {CHARA_INFO[World.new_chara][0]} level 1')
            #     stm.streamText('編成画面からパーティーに加えれます')
            #     World.new_chara = None
            _ = input("\n続けるには何かキーを入力:")
            raise StopIteration


# ステージ管理
class Stage(object): # DONE
    def __init__(self) -> None:
        self.stage_num: list[bool] = [True, False]
        self.all_skill_point: int = 0
        self.save: bool = False

    # ステージ表示
    def _show_stage(self) -> None:
        os.system(CLEAR)
        print(">>名前     : 番号")
        print(PARTITION)
        for i, num in enumerate(self.stage_num):
            if num:
                print(f">>ステージ{i+1}: {i+1}") 

    # ステージ選択 : 敵編成を返す
    def select_stage(self, Party:list[object], Me:object) -> list[object]:
        import stageinfo as si
        stage_func_list: list[object | int] = [
                                                si.one_one(), 
                                                si.one_two(), 
                                                si.one_three()
                                              ]
        while(True):
            # プレイ可能ステージ表示
            self._show_stage()
            key: str = input("\n>>ステージを選択してください(Pキーで味方ステータス表示, sキーでセーブ ,cキーでゲーム終了): ")
            try:
                key: int = int(key)
                # ステージ選択
                Enemy: list[object] = None
                for i, num in enumerate(self.stage_num):
                    if key == i+1 and num is True:
                        # ステージ敵セット
                        Enemy, self.now_stage, self.exp, self.skill_point = stage_func_list[i]
                        break
                if Enemy is None:
                    stm.stream_text("\n>>入力が間違っています。")
                    continue
                else:
                    break
                    
            except:
                # 条件分岐
                if key.lower() == 'p':
                    # メニュー表示
                    self._menu_show(Party)
                    continue
                # セーブ
                elif key.lower() == 's':
                    if Me.login_status:
                        self._save_progress(Me, Party)
                    else:
                        stm.stream_text("\n>>ゲストでログイン中です。セーブできません")
                    time.sleep(TIME)
                    os.system(CLEAR)
                    continue

                # ################
                # elif key.lower() == 'r':
                #     Party[0].hp = 0
                #     os.system('cls')
                #     continue
                # ###############
                        
                # ゲーム終了
                elif key.lower() == 'c':
                    self._end_game(Me, Party)
                else:
                    stm.stream_text("\n>>入力が間違っています。")
                    time.sleep(TIME)
                    os.system(CLEAR)
                    continue
        time.sleep(TIME)
        os.system(CLEAR)
        return Enemy

    # メニュー画面
    def _menu_show(self, Party:list[object]) -> None:
        os.system(CLEAR)
        # ステータス表示
        for num in Party:
            num.show_status()
        while(True):
            print("\n--メニュー--\n1: スキルポイント振り分け(ベータ版)\np: もどる\n")
            key: str = input(": ")
            if key == '1':
                self._skill_point_show(Party)
                break
            elif key.lower() == "p":
                os.system(CLEAR)
                break
            else:
                stm.stream_text("\n>>入力が間違っています。")

    # スキルポイント振り分け画面
    def _skill_point_show(self, Party:list[object]) -> None:
        while(True):
            os.system(CLEAR)
            stm.stream_text(f'>>現在のスキルポイントは{self.all_skill_point}です\n\n>>誰に振り分ける?(p: 戻る)')
            for i, num in enumerate(Party):
                print(f'{i+1}: {num.name}')
            key: str = input(': ')
            try:
                if int(key) < len(Party) or int(key) > 0:
                    break
            except:
                if key.lower() == 'p':
                    return
                stm.stream_text('>>入力が間違っています')
        self._point_assign(int(key)-1, Party)
        os.system(CLEAR)

    def _point_assign(self, key:int, Party:list[object]) -> None:
        # 選択
        while(True):
            os.system(CLEAR)
            stm.stream_text('>>どのステータスに振り分ける?')
            print('''1: HP
2: MP
3: STR
4: VTL
5: Mana
6: AATK
7: AMana
8: Speed''')
            status_select: str = input(": ")
            try:
                status_select = int(status_select)
            except:
                stm.stream_text('>>入力が間違っています')
            if int(status_select) < 9 or int(status_select) > 0:
                    break
            else:
                stm.stream_text('>>入力が間違っています')
        # 振り分け量入力
        while(True):
            os.system(CLEAR)
            stm.stream_text(f'>>どれだけ振り分ける?(現在のスキルポイント: {self.all_skill_point})')
            num: str = input(": ")
            try:
                if int(num) <= self.all_skill_point and int(num) >= 0:
                    break
                else:
                    stm.stream_text('>>入力値が多きすぎます')
            except:
                    stm.stream_text('>>入力が間違っています')
        Party[key].skill_point_assign(status_select, int(num))
        self.all_skill_point -= int(num)
        self.save = not self.save
        stm.stream_text('>>振り分け完了')

    # ゲーム終了
    def _end_game(self, Me:object, Party:list[object]) -> None:
        if not self.save and Me.login_status:
            stm.stream_text("\n>>進行状況がセーブされていません!")
            key: str = input(">>セーブしますか?[y/n] :")
            if key.lower() == 'y':
                self._save_progress(Me, Party)
        stm.stream_text("\n>>ゲームを終了します")
        time.sleep(TIME*2)
        os.system(CLEAR)
        import sys
        sys.exit()

    # セーブ
    def _save_progress(self, Me:object, Party:list[object]) -> None:
        Me.save_data(Party, self)
        self.save = not self.save
        stm.stream_text("\n>>セーブ完了")
        time.sleep(TIME)


# ゲーム説明本文
def game_explain() -> None:
    print(PARTITION*2)
    print('''
これはCUIで遊べるRPGゲームのようなものです。
実装状況: ステージ3まで
==属性について==
このゲームには光と闇の二属性があり(増える予定あり)
"光"と"闇"という名前の魔法も実装されています。
自分と同じ属性の相手に魔法を使うとあまり効果がありませんが、
違う属性の相手に魔法を使うとダメージが加算されます。
例) 自分(攻撃): 光　相手: 光　→　ダメージ↓
    自分(攻撃): 闇　相手: 光　→　ダメージ↑
属性チェンジをすると自分の属性を変えられるので属性を変えて大ダメージを狙うこともできます。
また敵はこの属性攻撃をしてきません。
''')    
    print(PARTITION*2)
    _ = input(">>続けるには何かキーを入力してください: ")


# ほんへ
if __name__ == "__main__":
    # ログイン処理
    Me: object = database.Database()
    # ゲスト、最初時
    if Me.login_status is False or Me.first is True:
        # ゲーム説明
        while(True):
            os.system(CLEAR)
            select: str = input('>>ゲーム説明を見ますか?[y/n]: ')
            if select.lower() == 'y':
                game_explain()
                break
            elif select.lower() == 'n':
                break
            else:
                print('>>入力が間違っています')
                time.sleep(TIME)

        # 初期味方編成
        Party: list[object] = []
        Party.append(PartyClass(*CHARA_INFO[0]))
        Party.append(PartyClass(*CHARA_INFO[1]))
        Party.append(PartyClass(*CHARA_INFO[2]))
        Party.append(PartyClass(*CHARA_INFO[3]))

        # 世界生成
        World: object = Stage()

        if not Me.login_status:
            World.save = None

    # セーブデータ読み込み
    else:
        Party, World = Me.set_data()

    #本編開始
    while(True):
        # ステージ選択
        Enemy: list[object] = World.select_stage(Party, Me)
        # 戦闘処理
        Battle(Party, Enemy, World)
        del Enemy
        # 次ステージ開放
        import stageinfo
        if World.now_stage < stageinfo.stage_num:
            World.stage_num[World.now_stage] = True
            World.stage_num.append(False)
        World.save = not World.save
        