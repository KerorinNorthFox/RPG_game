import os, sys, time, getpass, sqlite3, pickle, config#, bz2

TIME = 2
PROTOCOL = pickle.HIGHEST_PROTOCOL
obj_list = config.obj_list

class Database(object):
    def __init__(self):
        self.first = False
        # データベース接続
        try: db = ('users.db')
        except:
            print("\n>>データベースが存在しません")
            sys.exit()
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        # テーブルが存在しない場合テーブル作成
        cursor.execute("CREATE TABLE IF NOT EXISTS Users(id INTEGER PRIMARY KEY AUTOINCREMENT, username, password, hero_obj, fencer_obj, wizard_obj, sage_obj, demon_obj, world_obj)")
        cursor.close()

        # ログイン処理
        self.login_status = self._login(conn)
        if self.login_status is True:
            print(">>ログインしました")
        else:
            print(">>ゲストで始めます")
            self.first = True
        time.sleep(TIME)

        conn.commit()
        conn.close()

    # ログイン処理
    def _login(self, conn):
        while(True):
            os.system('cls')
            print('===ログインする===(ゲストで始める : g)')
            username = input(">>ユーザー名(アカウント作成 : pキー) : ")
            # アカウント作成
            if username.lower() == 'p':
                self._makeAccount(conn)
                continue
            elif username.lower() == 'g':
                return False
            real_pass = self._takePass(conn, username)
            if real_pass is False: continue # ユーザー名が存在しない場合continue
            password = getpass.getpass(prompt='>>パスワード : ')
            print(real_pass)
            if password != real_pass:
                print(">>パスワードが違います")
                time.sleep(TIME)
                continue
            else:
                self.username = username
                break
        return True

    # アカウント作成
    def _makeAccount(self, conn):
        cursor = conn.cursor()

        while(True):
            os.system('cls')
            print("===アカウント作成===")
            username = input(">>ユーザー名(やめるにはcキー) : ")
            if username.lower() == 'c': return
            # ユーザー名確認
            cursor.execute("SELECT username FROM Users where username = ?", ((username,)))
            if cursor.fetchone() is None: break
            else:
                print(">>既にそのユーザー名は使われています")
                time.sleep(TIME)
                continue
        password = input(">>パスワード : ")

        # ユーザー作成
        cursor.execute("INSERT INTO Users(username, password) VALUES(?, ?)", ((username, password)))
        print(">>アカウント作成完了")
        self.first = True
        time.sleep(TIME)

        cursor.close()

    # ユーザー名確認 ＆ パスワードを引き出し
    def _takePass(self, conn, username):
        cursor = conn.cursor()

        # ユーザー確認
        cursor.execute("SELECT password FROM Users where username = ?", ((username,)))
        password = cursor.fetchone()
        if password is None:
            print("\n>>アカウントが存在しません")
            time.sleep(TIME)
            return False
        cursor.execute("SELECT hero_obj FROM Users where username = ?", ((username,)))
        a = cursor.fetchone()
        if a[0] is None:
            self.first = True
        cursor.close()
        return password[0]

    # オブジェクト引き出し
    def setObj(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        Party = []

        cursor.execute("SELECT hero_obj FROM Users where username = ?", ((self.username,)))
        chara = cursor.fetchone()
        Party.append(pickle.loads(chara[0]))
        cursor.execute("SELECT fencer_obj FROM Users where username = ?", ((self.username,)))
        chara = cursor.fetchone()
        Party.append(pickle.loads(chara[0]))
        cursor.execute("SELECT wizard_obj FROM Users where username = ?", ((self.username,)))
        chara = cursor.fetchone()
        Party.append(pickle.loads(chara[0]))
        cursor.execute("SELECT sage_obj FROM Users where username = ?", ((self.username,)))
        chara = cursor.fetchone()
        Party.append(pickle.loads(chara[0]))

        cursor.execute("SELECT world_obj FROM Users where username = ?", ((self.username,)))
        world = cursor.fetchone()
        World = pickle.loads(world[0])

        cursor.close()
        conn.close()
        return Party, World

    # オブジェクト保存
    def saveObj(self, party_obj_list, world_obj):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        b = pickle.dumps(party_obj_list[0], PROTOCOL)
        cursor.execute("UPDATE Users SET hero_obj = ? WHERE username = ?", ((b, self.username)))
        b = pickle.dumps(party_obj_list[1], PROTOCOL)
        cursor.execute("UPDATE Users SET fencer_obj = ? WHERE username = ?", ((b, self.username)))
        b = pickle.dumps(party_obj_list[2], PROTOCOL)
        cursor.execute("UPDATE Users SET wizard_obj = ? WHERE username = ?", ((b, self.username)))
        b = pickle.dumps(party_obj_list[3], PROTOCOL)
        cursor.execute("UPDATE Users SET sage_obj = ? WHERE username = ?", ((b, self.username)))

        b = pickle.dumps(world_obj, PROTOCOL)
        cursor.execute("UPDATE Users SET world_obj = ? WHERE username = ?", ((b, self.username)))

        cursor.close()
        conn.commit()
        conn.close()
        world_obj.save = True

    # # オブジェクト→バイト列
    # def _obj_to_byte(self, obj):
    #     return bz2.compress(pickle.dumps(obj, PROTOCOL), 3)

    # # バイト列→オブジェクト
    # def _byte_to_obj(self, b):
    #     return pickle.loads(bz2.decompress(b))


if __name__ == '__main__':
    Database()