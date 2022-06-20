import requests
import os
import time
import pickle
import bz2


from character import CLEAR


TIME: int = 2


class Database(object):
    def __init__(self) -> None:
        # ログイン処理
        self.login_status: bool = self._login()

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

    # オブジェクト→バイト列
    def _obj_to_byte(self, obj:object) -> bytes:
        return bz2.compress(pickle.dumps(obj, pickle.HIGHEST_PROTOCOL), 3)

    # バイト列→オブジェクト
    def _byte_to_obj(self, b:bytes) -> object:
        return pickle.loads(bz2.decompress(b))