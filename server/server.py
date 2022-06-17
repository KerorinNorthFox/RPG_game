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

    b: bytes = obj_to_byte(world_obj)
    cursor.execute("UPDATE Users SET world_obj = ? WHERE username = ?", ((b, username)))

    cursor.close()
    conn.commit()
    conn.close()
    
    world_obj.save = True


