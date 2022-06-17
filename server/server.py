from flask import Flask, request, Response
import pickle
import bz2
import sqlite3


app = Flask(__name__)


# オブジェクト→バイト列
def obj_to_byte(self, obj:object) -> bytes:
    return bz2.compress(pickle.dumps(obj, pickle.HIGHEST_PROTOCOL), 3)

# バイト列→オブジェクト
def byte_to_obj(self, b:bytes) -> object:
    return pickle.loads(bz2.decompress(b))


@app.route("/save_obj", methods=['POST'])
def save_obj():
    user_data: str | bytes = request.data.decode('utf-8')
    username, party_obj_list, world_obj = user_data

    print(f">>Save objects by {username}")

    conn: object = sqlite3.connect('users.db')
    cursor: object = conn.cursor()

    b: bytes = obj_to_byte(party_obj_list[0])
    cursor.execute("UPDATE Users SET hero_obj = ? WHERE username = ?", ((b, username)))
    b: bytes = obj_to_byte(party_obj_list[1])
    cursor.execute("UPDATE Users SET fencer_obj = ? WHERE username = ?", ((b, username)))
    b: bytes = obj_to_byte(party_obj_list[2])
    cursor.execute("UPDATE Users SET wizard_obj = ? WHERE username = ?", ((b, username)))
    b: bytes = obj_to_byte(party_obj_list[3])
    cursor.execute("UPDATE Users SET sage_obj = ? WHERE username = ?", ((b, username)))

    world_obj.save = True
    b: bytes = obj_to_byte(world_obj)
    cursor.execute("UPDATE Users SET world_obj = ? WHERE username = ?", ((b, username)))

    cursor.close()
    conn.commit()
    conn.close()
    
    return Response(response=b, status=200)

@app.route("/set_obj", methods=['POST'])
def set_obj():
    username = request.data.decode('utf-8')
    

    conn: object = sqlite3.connect('users.db')
    cursor: object = conn.cursor()
    Party: list[object] = []

    cursor.execute("SELECT hero_obj FROM Users where username = ?", ((username,)))
    chara: tuple[bytes] = cursor.fetchone()
    Party.append(byte_to_obj(chara[0]))
    cursor.execute("SELECT fencer_obj FROM Users where username = ?", ((username,)))
    chara: tuple[bytes] = cursor.fetchone()
    Party.append(byte_to_obj(chara[0]))
    cursor.execute("SELECT wizard_obj FROM Users where username = ?", ((username,)))
    chara: tuple[bytes] = cursor.fetchone()
    Party.append(byte_to_obj(chara[0]))
    cursor.execute("SELECT sage_obj FROM Users where username = ?", ((username,)))
    chara: tuple[bytes] = cursor.fetchone()
    Party.append(byte_to_obj(chara[0]))

    cursor.execute("SELECT world_obj FROM Users where username = ?", ((username,)))
    world: tuple[bytes] = cursor.fetchone()
    World: object = byte_to_obj(world[0])

    cursor.close()
    conn.close()

    list_1 = [Party, World]
    list_1 = bz2.compress(list_1, 3)

    return Party, World

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
