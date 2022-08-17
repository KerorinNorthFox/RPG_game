from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from flask import Flask, request, Response
import sqlite3
import json
import base64
import threading


import commands as cm


conn: object = sqlite3.connect('users.db')
cursor: object = conn.cursor()
# テーブルが存在しない場合テーブル作成
cursor.execute("CREATE TABLE IF NOT EXISTS Users(id INTEGER PRIMARY KEY AUTOINCREMENT, username, password, hero_obj, fencer_obj, wizard_obj, sage_obj, demon_obj, world_obj)")
cursor.close()
conn.commit()
conn.close()


recipient_key = RSA.import_key(open("key/public.pem").read())
session_key = get_random_bytes(16)
file_in = open("key/encrypted_data.txt", "rb")
private_key = RSA.import_key(open("key/private.pem").read())


app: object = Flask(__name__)


# ネット接続確認
@app.route("/internet_connect", methods=['POST'])
def internet_connect():
    return Response(response='connected', status=200)


# ユーザーネーム確認
@app.route("/check_account_username", methods=['POST'])
def check_account_username():
    json_data: str = request.data.decode('utf-8')
    # 復号化
    username: str = decipher(json.loads(json_data))

    conn: object = sqlite3.connect('users.db')
    cursor: object = conn.cursor()
    
    cursor.execute("SELECT username FROM Users where username = ?", ((username,)))
    a = cursor.fetchone()

    cursor.close()
    conn.close()
    
    if a is None:
        # 暗号化
        data: dir[str] = cipher('True')
        return Response(response=json.dumps(data), status=200)
    elif a[0]:
        # 暗号化
        data: dir[str] = cipher('False')
        return Response(response=json.dumps(data), status=200)


# アカウント作成
@app.route("/make_account", methods=['POST'])
def make_account():
    json_str: str = request.data.decode('utf-8')
    # 復号化
    dir_data: str = decipher(json.loads(json_str))
    dir_data: dir[str] = json.loads(dir_data)

    conn: object = sqlite3.connect('users.db')
    cursor: object = conn.cursor()

    cursor.execute("INSERT INTO Users(username, password) VALUES(?, ?)", ((dir_data['username'], dir_data['password'])))
    
    cursor.execute("SELECT password FROM Users where username = ?", ((dir_data['username'],)))
    a = cursor.fetchone()

    cursor.close()
    conn.commit()
    conn.close()

    return Response(response=' ', status=200)
    

# パスワード確認
@app.route("/take_pass", methods=['POST'])
def take_pass():
    json_str: str = request.data.decode('utf-8')
    # 復号化
    username: str = decipher(json.loads(json_str))

    conn: object = sqlite3.connect('users.db')
    cursor: object = conn.cursor()

    # ユーザー確認
    cursor.execute("SELECT password FROM Users where username = ?", ((username,)))
    password: tuple[str] = cursor.fetchone()

    # パスワードが無い場合
    if password is None:
        data_dir: dir[str] = {'password' : None, 'bool' : '0'}
        data_json: str = json.dumps(data_dir)
        # 暗号化
        data = cipher(data_json)
        cursor.close()
        conn.close()

        return Response(response=json.dumps(data), status=200)

    cursor.execute("SELECT hero_obj FROM Users where username = ?", ((username,)))
    a: tuple[str] = cursor.fetchone()
    # セーブデータが無い場合
    if a[0] is None:
        data_dir: dir[str] = {'password' : password[0], 'bool' : '1'}
    else:
        data_dir: dir[str] = {'password' : password[0], 'bool' : '2'}
    
    cursor.close()
    conn.close()
        
    data_json: str = json.dumps(data_dir)
    # 暗号化
    data = cipher(data_json)

    return Response(response=json.dumps(data), status=200)


# データ引き出し
@app.route("/set_data", methods=['POST'])
def set_data() -> str:
    username: str = request.data.decode('utf-8')
    # 復号化
    username: str = decipher(json.loads(username))

    print(f"\n>>Load objects by {username}")

    conn: object = sqlite3.connect('users.db')
    cursor: object = conn.cursor()
    Party: list[object] = []

    cursor.execute("SELECT hero_obj FROM Users where username = ?", ((username,)))
    chara: tuple[bytes] = cursor.fetchone()
    Party.append(chara[0])
    cursor.execute("SELECT fencer_obj FROM Users where username = ?", ((username,)))
    chara: tuple[bytes] = cursor.fetchone()
    Party.append(chara[0])
    cursor.execute("SELECT wizard_obj FROM Users where username = ?", ((username,)))
    chara: tuple[bytes] = cursor.fetchone()
    Party.append(chara[0])
    cursor.execute("SELECT sage_obj FROM Users where username = ?", ((username,)))
    chara: tuple[bytes] = cursor.fetchone()
    Party.append(chara[0])

    cursor.execute("SELECT world_obj FROM Users where username = ?", ((username,)))
    world: tuple[bytes] = cursor.fetchone()
    World: bytes = world[0]

    cursor.close()
    conn.close()

    user_data: str = {'party_str_list' : Party, 'world_str' : World}

    # 暗号化
    data: dir[str] = cipher(json.dumps(user_data))

    return json.dumps(data)  # 中身はすべてバイト列、向こうで戻すこと


# データ保存
@app.route("/save_data", methods=['POST'])
def save_data():
    json_str: str = request.data.decode('utf-8') # jsonデータ
    # 復号化
    data = decipher(json.loads(json_str))
    user_data: dict = json.loads(data)

    # 受け取ったjsonの文字列をバイト列に戻す
    username, party_str_list, world_str = user_data['username'], user_data['party_str_list'], user_data['world_str']

    print(f">>Save objects by {username}")

    conn: object = sqlite3.connect('users.db')
    cursor: object = conn.cursor()

    cursor.execute("UPDATE Users SET hero_obj = ? WHERE username = ?", ((party_str_list[0], username)))
    cursor.execute("UPDATE Users SET fencer_obj = ? WHERE username = ?", ((party_str_list[1], username)))
    cursor.execute("UPDATE Users SET wizard_obj = ? WHERE username = ?", ((party_str_list[2], username)))
    cursor.execute("UPDATE Users SET sage_obj = ? WHERE username = ?", ((party_str_list[3], username)))

    cursor.execute("UPDATE Users SET world_obj = ? WHERE username = ?", ((world_str, username)))

    cursor.close()
    conn.commit()
    conn.close()
    
    return Response(response=" ", status=200)


# string型のバイト列をバイト列に
def encoded_string_to_bytes(bytes_str):
    return base64.b64decode(bytes_str)


# バイト列をstring型のバイト列に
def bytes_to_encoded_string(obj_bytes):
    # エンコード
    obj_encode_bytes: bytes = base64.b64encode(obj_bytes)
    # string型でデコード
    return obj_encode_bytes.decode('utf-8')


# 暗号化
def cipher(text:str) -> dir:
    # 暗号化準備
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    
    # 暗号化
    ciphertext, tag = cipher_aes.encrypt_and_digest(text.encode('utf-8'))
    
    # 通信できるようにバイト列を文字列に
    enc_session_key = bytes_to_encoded_string(enc_session_key)
    nonce = bytes_to_encoded_string(cipher_aes.nonce)
    tag = bytes_to_encoded_string(tag)
    ciphertext = bytes_to_encoded_string(ciphertext)
    
    data = {'enc_session_key':enc_session_key, 'nonce':nonce, 'tag':tag, 'ciphertext':ciphertext}

    return data


# 復号化
def decipher(data:str) -> str:
    enc_session_key, nonce  = encoded_string_to_bytes(data['enc_session_key']), encoded_string_to_bytes(data['nonce'])
    tag, ciphertext = encoded_string_to_bytes(data['tag']), encoded_string_to_bytes(data['ciphertext'])

    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)    
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    text = cipher_aes.decrypt_and_verify(ciphertext, tag)

    return text.decode('utf-8')

#----------------------------------------------------------

# サーバースタート
def server():
    app.run(host='0.0.0.0', port=8080, threaded=True)


# コマンド
def loop():
    while(True):
        com = input(">>")
        # ユーザー一覧を見る
        if com == '!users':
            cm.user_show()


if __name__ == '__main__':
    thread1 = threading.Thread(target=server)
    thread2 = threading.Thread(target=loop)
    thread1.start()
    thread2.start()

    

