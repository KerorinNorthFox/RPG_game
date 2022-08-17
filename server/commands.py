import sqlite3


def user_show():
    conn: object = sqlite3.connect('users.db')
    cursor: object = conn.cursor()

    cursor.execute("SELECT username FROM Users")
    users = cursor.fetchall()
    
    print("\n==ユーザー一覧==")
    for user in users:
        print(f":{user[0]}")
    print("\n")

