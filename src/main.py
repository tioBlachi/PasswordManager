from argon2 import PasswordHasher
import sqlite3


def init_db():
    conn = sqlite3.connect('passwords.db')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        PRIMARY KEY id INTEGER NOT NULL AUTOINCREMENT),
        username VARCHAR(25) NOT NULL,
        vault_key VARCHAR(255) NOT NULL
        );
    ''')
    conn.close()


def reset_db(db_name: str = 'passwords.db')
    conn = sqlite3.connect('passwords.db')
    conn.execute(f'DROP TABLE IF EXISTS {db_name}')
    conn.close()


def add_user(username: str, vault_key: str, db_name: str = 'passwords.db'):
    conn = sqlite3.connect(db_name)
    conn.execute('''
    INSERT INTO users (username, vault_key) VALUES (?, ?)
    (username, vault_key)
    ''')
    conn.commit()
    conn.close()


ph = PasswordHasher()

hash = ph.hash("blas is the best!")

print(hash)

try:
    if ph.verify(hash, "blas is the best"):
        print("Password verified!")
except:
    print("Password verification failed!")
