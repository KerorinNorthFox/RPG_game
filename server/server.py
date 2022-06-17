from flask import Flask, request, Response
import sqlite3
import json


app = Flask(__name__)


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
