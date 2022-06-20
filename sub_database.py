import os
import time
import sqlite3
import pickle
import bz2
import requests

from character import CLEAR


TIME: int = 2


class Database(object):
    def __init__(self) -> None:
        self.first: bool = False

        # データベース接続
        try:
            db: object = ('users.db')
        except:
            print("\n>>データベースが存在しません")
            import sys
            sys.exit()
        conn: object = sqlite3.connect(db)
        cursor: object = conn.cursor()
        # テーブルが存在しない場合テーブル作成
        cursor.execute("CREATE TABLE IF NOT EXISTS Users(id INTEGER PRIMARY KEY AUTOINCREMENT, username, password, hero_obj, fencer_obj, wizard_obj, sage_obj, demon_obj, world_obj)")
        cursor.close()

        # ログイン処理
        self.login_status: bool = self._login(conn)
        if self.login_status:
            print("\n>>ログインしました")
        else:
            print("\n>>ゲストで始めます")
            self.first = True
        time.sleep(TIME)

        conn.commit()
        conn.close()

    # ログイン処理
    def _login(self, conn:object) -> bool:
        while(True):
            os.system(CLEAR)

            print('===ログインする===(ゲストで始める: g)')
            username: str = input(">>ユーザー名(アカウント作成: pキー): ")

            # アカウント作成
            if username.lower() == 'p':
                self._make_account(conn)
                continue
            elif username.lower() == 'g':
                return False
            real_pass: str = self._take_pass(conn, username)
            if not real_pass:
                # ユーザー名が存在しない場合continue
                continue

            import getpass
            password: str = getpass.getpass(prompt='>>パスワード: ')
            if password != real_pass:
                print("\n>>パスワードが違います")
                time.sleep(TIME)
                continue
            else:
                self.username: str = username
                self.password: str = password
                break
        return True

    # アカウント作成
    def _make_account(self, conn:object) -> None:
        cursor: object = conn.cursor()

        while(True):
            os.system(CLEAR)
            
            print("===アカウント作成===")
            username: str = input(">>ユーザー名(やめるにはcキー): ")
            if username.lower() == 'c':
                return
            # ユーザー名確認
            cursor.execute("SELECT username FROM Users where username = ?", ((username,)))
            if cursor.fetchone() is None:
                break
            else:
                print("\n>>既にそのユーザー名は使われています")
                time.sleep(TIME)
                continue
        password: str = input(">>パスワード: ")

        # ユーザー作成
        cursor.execute("INSERT INTO Users(username, password) VALUES(?, ?)", ((username, password)))
        print("\n>>アカウント作成完了")
        self.first = True
        time.sleep(TIME)

        cursor.close()

    # ユーザー名確認 ＆ パスワードを引き出し
    def _take_pass(self, conn:object, username:str) -> str:
        cursor: object = conn.cursor()

        # ユーザー確認
        cursor.execute("SELECT password FROM Users where username = ?", ((username,)))
        password: tuple[str] = cursor.fetchone()
        if password is None:
            print("\n>>アカウントが存在しません")
            time.sleep(TIME)
            return False
        cursor.execute("SELECT hero_obj FROM Users where username = ?", ((username,)))
        a: tuple[str] = cursor.fetchone()
        if a[0] is None:
            self.first = True
        cursor.close()
        return password[0]

    # オブジェクト引き出し
    def set_obj(self) -> object:
        conn: object = sqlite3.connect('users.db')
        cursor: object = conn.cursor()
        Party: list[object] = []

        cursor.execute("SELECT hero_obj FROM Users where username = ?", ((self.username,)))
        chara: tuple[bytes] = cursor.fetchone()
        Party.append(self._byte_to_obj(chara[0]))
        cursor.execute("SELECT fencer_obj FROM Users where username = ?", ((self.username,)))
        chara: tuple[bytes] = cursor.fetchone()
        Party.append(self._byte_to_obj(chara[0]))
        cursor.execute("SELECT wizard_obj FROM Users where username = ?", ((self.username,)))
        chara: tuple[bytes] = cursor.fetchone()
        Party.append(self._byte_to_obj(chara[0]))
        cursor.execute("SELECT sage_obj FROM Users where username = ?", ((self.username,)))
        chara: tuple[bytes] = cursor.fetchone()
        Party.append(self._byte_to_obj(chara[0]))

        cursor.execute("SELECT world_obj FROM Users where username = ?", ((self.username,)))
        world: tuple[bytes] = cursor.fetchone()
        World: object = self._byte_to_obj(world[0])

        cursor.close()
        conn.close()
        return Party, World

    # オブジェクト保存
    def save_obj(self, party_obj_list:list[object], world_obj:object) -> None:
        conn: object = sqlite3.connect('users.db')
        cursor: object = conn.cursor()

        b: bytes = self._obj_to_byte(party_obj_list[0])
        cursor.execute("UPDATE Users SET hero_obj = ? WHERE username = ?", ((b, self.username)))
        b: bytes = self._obj_to_byte(party_obj_list[1])
        cursor.execute("UPDATE Users SET fencer_obj = ? WHERE username = ?", ((b, self.username)))
        b: bytes = self._obj_to_byte(party_obj_list[2])
        cursor.execute("UPDATE Users SET wizard_obj = ? WHERE username = ?", ((b, self.username)))
        b: bytes = self._obj_to_byte(party_obj_list[3])
        cursor.execute("UPDATE Users SET sage_obj = ? WHERE username = ?", ((b, self.username)))

        b: bytes = self._obj_to_byte(world_obj)
        cursor.execute("UPDATE Users SET world_obj = ? WHERE username = ?", ((b, self.username)))

        cursor.close()
        conn.commit()
        conn.close()
        
        world_obj.save = True

    # オブジェクト→バイト列
    def _obj_to_byte(self, obj:object) -> bytes:
        return bz2.compress(pickle.dumps(obj, pickle.HIGHEST_PROTOCOL), 3)

    # バイト列→オブジェクト
    def _byte_to_obj(self, b:bytes) -> object:
        return pickle.loads(bz2.decompress(b))


# ログインテスト
if __name__ == '__main__':
    Database()