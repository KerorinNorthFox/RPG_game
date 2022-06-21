import requests
import os
import time
import pickle
import bz2
import base64
import json


from character import CLEAR


URL: str = 'http://localhost:8080'
TIME: int = 2


class Database(object):
    def __init__(self) -> None:
        # ログイン処理
        self.login_status: bool = self._login()
        if self.login_status:
            print("\n>>ログインしました")
        else:
            print("\n>>ゲストで始めます")
            self.first = True
        time.sleep(TIME)

    # ログイン処理
    def _login(self) -> bool:
        # ネット接続＆サーバー接続確認
        try:
            connect: bool = self._internet_connection_test()
            if not connect:
                return False
        except:
            return False
        while(True):
            os.system(CLEAR)

            print('===ログインする===(ゲストで始める: g)')
            username: str = input(">>ユーザー名(アカウント作成: pキー): ")

            # アカウント作成
            if username.lower() == 'p':
                self._make_account()
                continue
            elif username.lower() == 'g':
                return False
            real_pass: str = self._take_pass(username)
            print(real_pass)
            if not real_pass:
                print("\n>>アカウントが存在しません")
                time.sleep(TIME)
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

    # インターネット接続確認
    def _internet_connection_test(self) -> bool:
        res: object = requests.post(URL+"/internet_connect")
        if not res.status_code == 200:
            return False
        print(res.text)
        return True

    # アカウント作成
    def _make_account(self) -> None:
        while(True):
            os.system(CLEAR)
                
            print("===アカウント作成===")
            username: str = input(">>ユーザー名(やめるにはcキー): ")
            if username.lower() == 'c':
                return
            # ユーザー名確認
            res: object = requests.post(URL+"/check_account_username", data=username)
            print(res.text)
            if res.text == 'True':
                break
            else:
                print("\n>>既にそのユーザー名は使われています")
                time.sleep(TIME)
                continue

        password: str = input(">>パスワード: ")

        # ユーザー作成
        dir_data: dir[str] = {'username' : username, 'password' : password}
        _ = requests.post(URL+"/make_account", data=json.dumps(dir_data))
        
        print("\n>>アカウント作成完了")
        self.first = True
        time.sleep(TIME)
        
    # ユーザー名確認 ＆ パスワードを引き出し
    def _take_pass(self, username:str) -> str:
        res: object = requests.post(URL+"/take_pass", data=username)
        res_dir: dir[str | bool] = res.json()
        if res_dir['bool']:
            self.first = True
        else:
            return False
        return res_dir['password']

    # データ引き出し
    def set_data(self) -> object:
        json_str: str = requests.post(URL+"/set_data", data=self.username)
        user_data: dir[list[bytes] | bytes] = json_str.json()

        Party: list[object] = []
        for obj_bytes in user_data['party_obj_list']:
            obj: object = self._byte_to_obj(obj_bytes)
            Party.append(obj)

        World: object = self._byte_to_obj(user_data['world_obj'])

        return Party, World

    # データ保存
    def save_data(self, party_obj_list:list[object], world_obj:object):
        party_str_list: list[str] = []
        for obj in party_obj_list:
            # バイト列に変換
            obj_bytes: bytes = self._obj_to_byte(obj)
            obj_encode_str: str = self._bytes_to_encoded_string(obj_bytes)
            party_str_list.append(obj_encode_str)
        
        world_bytes: bytes = self._obj_to_byte(world_obj)
        world_str: str = self._bytes_to_encoded_string(world_bytes)

        user_data = {'username' : self.username, 'party_str_list' : party_str_list, 'world_str' : world_str}
        json_str = json.dumps(user_data)

        _ = requests.post(URL+'/save_data', data=json_str)

    # バイト列をstring型のバイト列に
    def _bytes_to_encoded_string(self, bytes):
        # エンコード
        obj_encode_bytes: bytes = base64.b64encode(bytes)
        # string型でデコード
        return obj_encode_bytes.decode('utf-8')

    # オブジェクト→バイト列
    def _obj_to_byte(self, obj:object) -> bytes:
        return bz2.compress(pickle.dumps(obj, pickle.HIGHEST_PROTOCOL), 3)

    # バイト列→オブジェクト
    def _byte_to_obj(self, b:bytes) -> object:
        return pickle.loads(bz2.decompress(b))

if __name__ == '__main__':
    Database()
