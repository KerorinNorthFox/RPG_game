from flask import Flask, request, Response
import sqlite3
import json


conn: object = sqlite3.connect('users.db')
cursor: object = conn.cursor()
# テーブルが存在しない場合テーブル作成
cursor.execute("CREATE TABLE IF NOT EXISTS Users(id INTEGER PRIMARY KEY AUTOINCREMENT, username, password, hero_obj, fencer_obj, wizard_obj, sage_obj, demon_obj, world_obj)")
cursor.close()
conn.commit()
conn.close()


app: object = Flask(__name__)


# ネット接続確認
@app.route("/internet_connect", methods=['POST'])
def internet_connect():
    return Response(response='connected', status=200)

# ユーザーネーム確認
@app.route("/check_account_username", methods=['POST'])
def check_account_username():
    username: str = request.data.decode('utf-8')

    conn: object = sqlite3.connect('users.db')
    cursor: object = conn.cursor()
    
    cursor.execute("SELECT username FROM Users where username = ?", ((username,)))
    a = cursor.fetchone()
    print(a)
    cursor.close()
    conn.close()
    if a is None:
        return Response(response='True', status=200)
    elif a[0]:
        return Response(response='False', status=200)

# アカウント作成
@app.route("/make_account", methods=['POST'])
def make_account():
    json_str = request.data.decode('utf-8')
    dir_data = json.loads(json_str)

    print(dir_data['username'])
    print(dir_data['password'])

    conn: object = sqlite3.connect('users.db')
    cursor: object = conn.cursor()

    cursor.execute("INSERT INTO Users(username, password) VALUES(?, ?)", ((dir_data['username'], dir_data['password'])))

    cursor.execute("SELECT password FROM Users where username = ?", ((dir_data['username'],)))
    a = cursor.fetchone()
    print(f'\n{a}')

    cursor.close()
    conn.commit()
    conn.close()

    return Response(response='DONE', status=200)
    

# パスワード確認
@app.route("/take_pass", methods=['POST'])
def take_pass():
    username: str = request.data.decode('utf-8')

    conn: object = sqlite3.connect('users.db')
    cursor: object = conn.cursor()

    print(username)
    # ユーザー確認
    cursor.execute("SELECT password FROM Users where username = ?", ((username,)))
    password: tuple[str] = cursor.fetchone()
    print(password)
    if password is None:
        data_dir: dir[str | bool] = {'password' : None, 'bool' : False}
        data_json: str = json.dumps(data_dir)
        cursor.close()
        conn.close()
        return Response(response=data_json, status=200)

    cursor.execute("SELECT hero_obj FROM Users where username = ?", ((username,)))
    a: tuple[str] = cursor.fetchone()
    if a[0] is None:
        data_dir: dir[str | bool] = {'password' : password[0], 'bool' : True}
        data_json: str = json.dumps(data_dir)
    cursor.close()
    conn.close()
    return Response(response=data_json, status=200)

# データ保存
@app.route("/save_obj", methods=['POST'])
def save_obj():
    json_str: str = request.data.decode('utf-8') # jsonデータ
    user_data: dict = json.loads(json_str)
    username, party_obj_list, world_obj_bytes = user_data['username'], user_data['party_obj_list'], user_data['world_obj']

    print(f">>Save objects by {username}")

    conn: object = sqlite3.connect('users.db')
    cursor: object = conn.cursor()

    b: bytes = party_obj_list[0]
    cursor.execute("UPDATE Users SET hero_obj = ? WHERE username = ?", ((b, username)))
    b: bytes = party_obj_list[1]
    cursor.execute("UPDATE Users SET fencer_obj = ? WHERE username = ?", ((b, username)))
    b: bytes = party_obj_list[2]
    cursor.execute("UPDATE Users SET wizard_obj = ? WHERE username = ?", ((b, username)))
    b: bytes = party_obj_list[3]
    cursor.execute("UPDATE Users SET sage_obj = ? WHERE username = ?", ((b, username)))

    # world_obj.save = True # ←忘れない!!
    cursor.execute("UPDATE Users SET world_obj = ? WHERE username = ?", ((world_obj_bytes, username)))

    cursor.close()
    conn.commit()
    conn.close()
    
    return Response(response="DONE", status=200)

# データ引き出し
@app.route("/set_obj", methods=['POST'])
def set_obj() -> str:
    username: str = request.data.decode('utf-8')

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
    user_data: str = {'username' : username, 'party_obj_list' : Party, 'world_obj' : World}

    return json.dumps(user_data)  # 中身はすべてバイト列、向こうで戻すこと

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
