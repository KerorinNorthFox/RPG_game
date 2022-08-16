from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import requests
import os
import time
import pickle
import bz2
import base64
import json


from source.character import CLEAR


URL: str = 'http://localhost:8080'
TIME: int = 2


recipient_key = RSA.import_key(open("source/public.pem").read())
session_key = get_random_bytes(16)
file_in = open("encrypted_data.txt", "rb")
private_key = RSA.import_key(open("source/private.pem").read())


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
                print(">>サーバー接続で問題が発生しました\n")
                return False
        except:
            print(">>サーバー接続で問題が発生しました\n")
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
            # 暗号化
            data: dir[str] = self._cipher(username)
            # ユーザー名確認
            res: object = requests.post(URL+"/check_account_username", data=json.dumps(data))
            # 復号化
            text: str = self._decipher(json.loads(res.text))
            if text == 'True':
                break
            else:
                print("\n>>既にそのユーザー名は使われています")
                time.sleep(TIME)
                continue

        password: str = input(">>パスワード: ")

        # ユーザー作成
        dir_data: dir[str] = {'username' : username, 'password' : password}
        # 暗号化
        data: dir[str] = self._cipher(json.dumps(dir_data))
        _ = requests.post(URL+"/make_account", data=json.dumps(data))
        
        print("\n>>アカウント作成完了")
        time.sleep(TIME)
        
    # ユーザー名確認 ＆ パスワードを引き出し
    def _take_pass(self, username:str) -> str:
        # 暗号化
        data: dir[str] = self._cipher(username)
        res: object = requests.post(URL+"/take_pass", data=json.dumps(data))
        # 復号化
        res_dir: str = self._decipher(res.json())
        res_dir = json.loads(res_dir)

        # アカウントはあるがセーブデータ無し
        if res_dir['bool'] == '1':
            self.first = True
        # セーブデータ有り
        elif res_dir['bool'] == '2':
            self.first = False
        # アカウント無し
        elif res_dir['bool'] == '0':
            return False
        
        return res_dir['password']

    # データ引き出し
    def set_data(self) -> object:
        # 暗号化
        data = self._cipher(self.username)
        json_str: object = requests.post(URL+"/set_data", data=json.dumps(data))
        # 復号化
        user_data: str = self._decipher(json_str.json())
        user_data = json.loads(user_data)

        # 文字列からバイト列に
        party_bytes_list = []
        party_bytes_list = [self._encoded_string_to_bytes(bytes_str) for bytes_str in user_data['party_str_list']]
        world_bytes = self._encoded_string_to_bytes(user_data['world_str'])

        # バイト列からオブジェクトに
        Party: list[object] = []
        for obj_bytes in party_bytes_list:
            obj: object = self._byte_to_obj(obj_bytes)
            Party.append(obj)

        World: object = self._byte_to_obj(world_bytes)

        return Party, World

    # データ保存
    def save_data(self, party_obj_list:list[object], world_obj:object):
        party_str_list: list[str] = []
        for obj in party_obj_list:
            # バイト列に変換
            obj_bytes: bytes = self._obj_to_byte(obj)
            # バイト列から文字列に
            obj_encode_str: str = self._bytes_to_encoded_string(obj_bytes)
            party_str_list.append(obj_encode_str)
        
        # 上と同様
        world_bytes: bytes = self._obj_to_byte(world_obj)
        world_str: str = self._bytes_to_encoded_string(world_bytes)

        user_data = {'username' : self.username, 'party_str_list' : party_str_list, 'world_str' : world_str}

        # 暗号化
        data = self._cipher(json.dumps(user_data))

        _ = requests.post(URL+'/save_data', data=json.dumps(data))

    # string型のバイト列をバイト列に
    def _encoded_string_to_bytes(self, bytes_str):
        return base64.b64decode(bytes_str)

    # バイト列をstring型のバイト列に
    def _bytes_to_encoded_string(self, obj_bytes):
        # エンコード
        obj_encode_bytes: bytes = base64.b64encode(obj_bytes)
        # string型でデコード
        return obj_encode_bytes.decode('utf-8')

    # オブジェクト→バイト列
    def _obj_to_byte(self, obj:object) -> bytes:
        return bz2.compress(pickle.dumps(obj, pickle.HIGHEST_PROTOCOL), 3)

    # バイト列→オブジェクト
    def _byte_to_obj(self, b:bytes) -> object:
        return pickle.loads(bz2.decompress(b))

    # 暗号化
    def _cipher(self, text:str) -> dir:
        # 暗号化準備
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        enc_session_key = cipher_rsa.encrypt(session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        
        # 暗号化
        ciphertext, tag = cipher_aes.encrypt_and_digest(text.encode('utf-8'))
        
        # 通信できるようにバイト列を文字列に
        enc_session_key = self._bytes_to_encoded_string(enc_session_key)
        nonce = self._bytes_to_encoded_string(cipher_aes.nonce)
        tag = self._bytes_to_encoded_string(tag)
        ciphertext = self._bytes_to_encoded_string(ciphertext)
        
        data = {'enc_session_key':enc_session_key, 'nonce':nonce, 'tag':tag, 'ciphertext':ciphertext}

        return data

    # 復号化
    def _decipher(self, data:str) -> str:
        enc_session_key, nonce  = self._encoded_string_to_bytes(data['enc_session_key']), self._encoded_string_to_bytes(data['nonce'])
        tag, ciphertext = self._encoded_string_to_bytes(data['tag']), self._encoded_string_to_bytes(data['ciphertext'])

        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)    
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        text = cipher_aes.decrypt_and_verify(ciphertext, tag)

        return text.decode('utf-8')


if __name__ == '__main__':
    Database()
