import os
import time
import random

import config
from character import *
import streamtextmodule as stm

CHARA_INFO = config.chara_info
MAGIC_NAME: list[str] = config.magic_name

class Battle(object):
    def __init__(self, Party, Enemy, World):
        self.PARTYLENGTH: int = len(Party) # 味方の人数
        self.ENEMYLENGTH: int = len(Enemy) # 敵の人数
        self.NOWTURN: int = 1 # 現在のターン
        print(max(self.PARTYLENGTH, self.ENEMYLENGTH))

        stm.stream_text(">>戦闘開始\n")
        # 敵とエンカウント表示
        self._encountEnemy(Enemy) 
        # メインループ開始
        try:
            while(True):
                # 表示リセット
                os.system('cls')
                # 現在のターン表示
                stm.stream_text(f"\n>>現在のターン : {self.NOWTURN}\n")
                time.sleep(TIME)
                # 敵味方ステータス表示
                self._showStatuses(Party, Enemy)
                print(PARTITION*2)

                # 味方のターン
                for chara in Party:
                    # 死亡判定
                    if chara.alive is False:
                        chara.way = None
                        chara.target = None
                        continue
                    # 行動選択
                    chara.way = self._myTurn(chara)
                    # ターゲット選択
                    if chara.way == 1: # 攻撃
                        chara.target = self._partySelectTarget(Enemy, "攻撃", "倒した敵", self.ENEMYLENGTH)
                    elif chara.way == 2: # 防御
                        chara.target = None
                    elif chara.way == 3: # 魔法
                        chara.my_magic = self._selectMagic(chara)
                        if "ヒール" in chara.magic[chara.my_magic]:
                            chara.target = self._partySelectTarget(Party, "ヒール", "倒れた味方", self.PARTYLENGTH)
                        else:
                            chara.target = self._partySelectTarget(Enemy, "魔法攻撃", "倒した敵", self.ENEMYLENGTH)
                    elif chara.way == 4: # 属性変更
                        self._changeElement(chara)
                        chara.target = None
                    else: # 逃走
                        stm.stream_text("\n>>一行は逃げ出した")
                        World.now_stage = 0
                        time.sleep(TIME)
                        os.system('cls')
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
                    chara.target = self._enemySelectTarget(Party)

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
                            print(pt_ct)
                            print('do')
                            # 死亡判定
                            if Party[pt_ct].way == None or Party[pt_ct].alive == False or Party[pt_ct].target == None:
                                print('die')
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
                                Party[pt_ct].physicalAttack(Enemy[Party[pt_ct].target], False)
                            elif Party[pt_ct].way == 3: # 魔法攻撃
                                # 魔法レート設定
                                magic_rate = self._setMagicRate(Party[pt_ct], Enemy)
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
                for chara in Party: chara.defence = False
        except StopIteration: pass
        
    # 敵とエンカウント表示
    def _encountEnemy(self, Enemy):
        for num in Enemy: print(f">>{num.name}が現れた!")
        time.sleep(TIME*2)

    # 敵味方のステータスを表示
    def _showStatuses(self, Party, Enemy):
        for x in Party: x.showStatus()
        for y in Enemy: y.showStatus()
        time.sleep(TIME)

    # 行動選択
    def _myTurn(self, chara):
        while(True):
            stm.stream_text(f"\n--{chara.name}はどうする?--")
            time.sleep(TIME/2)
            print(f"1 : 攻撃\n2 : 防御\n3 : 魔法\n4 : 属性チェンジ\n5 : 逃げる")
            select = input("\n: ")
            try:
                select = int(select)
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
    def _selectMagic(self, chara):
        while(True):
            stm.stream_text("\n--どの魔法を使う?--")
            time.sleep(TIME)
            for i, num in enumerate(chara.magic):
                print(f">>{i+1} : {num}")
            select = input("\n: ")
            try:
                select = int(select)
                if select > len(chara.magic) or select <= 0:
                    stm.stream_text("\n>>入力が間違っています。")
                    time.sleep(TIME)
                    continue
                break
            except ValueError:
                stm.stream_text("\n>>入力が間違っています。")
                time.sleep(TIME)
        return select-1

    # 属性変更
    def _changeElement(self, chara):
        stm.stream_text(f"\n>>{chara.name}は属性を変更した!")
        chara.element = not chara.element

    # 味方ターゲット選択
    def _partySelectTarget(self, Enemy, text_1, text_2, length):
        while(True):
            stm.stream_text(f"\n>>誰に{text_1}する? : ")
            for i, chara in enumerate(Enemy):
                print(f"{i+1} : {chara.name}")
            select = input("\n: ")
            try:
                select = int(select)
                if select > length or select <= 0:
                    stm.stream_text("\n>>入力が間違っています。")
                    time.sleep(TIME)
                    continue
                elif Enemy[select-1].hp <= 0:
                    stm.stream_text(f"\n>>{text_2}に攻撃はできません")
                    time.sleep(TIME)
                    continue
                break
            except ValueError:
                stm.stream_text("\n>>入力が間違っています。")
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
    def _setMagicRate(self, chara, Enemy):
        # ヒールの場合例外
        if "ヒール" in chara.magic[chara.my_magic]:
            magic_rate = 1.4
        else:
            if chara.element == Enemy[chara.target].element: magic_rate = 1.0
            else: magic_rate = 1.4
        return magic_rate

    # 魔法種類別処理
    def _magicProcess(self, Party, Enemy, i, magic_rate):
        if MAGIC_NAME[1] == Party[i].magic[Party[i].my_magic]: # 初級ヒール
            Party[i].heal(Party[Party[i].target], 1.0)
        elif MAGIC_NAME[2] == Party[i].magic[Party[i].my_magic]: # 中級ヒール
            Party[i].heal(Party[Party[i].target], 1.5)
        elif MAGIC_NAME[3] == Party[i].magic[Party[i].my_magic]: # 上級ヒール
            Party[i].heal(Party[Party[i].target], 2.0)
        elif MAGIC_NAME[4] == Party[i].magic[Party[i].my_magic]: # 光
            if Enemy[Party[i].target].element is False: rate = 1.3
            else: rate = 0.2
            Party[i].magicalAttack(Enemy[Party[i].target], Enemy[i].defence, magic_rate * rate)
        elif MAGIC_NAME[5] == Party[i].magic[Party[i].my_magic]:# 闇
            if Enemy[Party[i].target].element is True: rate = 1.3
            else: rate = 0.2
            Party[i].magicalAttack(Enemy[Party[i].target], Enemy[i].defence, magic_rate * rate)
        else: # 通常
            Party[i].magicalAttack(Enemy[Party[i].target], Enemy[i].defence, magic_rate)

    # 防御表示
    def _showDefense(self, Party):
        for chara in Party:
            if chara.way == 2:
                stm.stream_text(f"\n>>{chara.name}は防御の姿勢をとった")
                chara.defence = True

    # 戦闘終了
    def _endBattle(self, Party, Enemy, World):
        World.save = False
        killed_party_len: int = len([0 for chara in Party if chara.hp == 0])
        killed_enemy_len: int = len([0 for chara in Enemy if chara.hp == 0])

        # 終了判定
        if killed_party_len == self.PARTYLENGTH or killed_enemy_len == self.ENEMYLENGTH:
            time.sleep(TIME)
            os.system('cls')
            stm.stream_text("\n>>戦闘終了")
            time.sleep(TIME)

            if killed_party_len < killed_enemy_len:
                print(f"\n>>勝利!")
                exp_level = 'victory'
            elif killed_party_len > killed_enemy_len:
                print(f"\n>>敗北")
                exp_level = 'defeat'
            else:
                print("\n>>引き分け")
                exp_level = 'draw'
            time.sleep(TIME)

            if exp_level == 'victory': exp = World.exp
            elif exp_level == 'defeat': exp = World.exp / 5
            elif exp_level == 'draw': exp = World.exp / 2

            # 経験値加算
            stm.stream_text(f'\nそれぞれが{exp}exp手に入れた')
            time.sleep(TIME)
            for chara in Party:
                chara.addExp(exp)

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

