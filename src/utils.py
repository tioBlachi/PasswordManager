import sqlite3, os


def init_db(db_name: str = "passwords.db"):
    conn = sqlite3.connect(db_name)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            vault_key TEXT NOT NULL
        );
        """
    )
    conn.close()
    return conn


def reset_db(db_name: str = "passwords.db"):
    if os.path.exists(db_name):
        os.remove(db_name)
    return None


def add_user(username: str, vault_key: str, db_name: str = "passwords.db"):
    conn = sqlite3.connect(db_name)
    conn.execute(
        """
    INSERT INTO users (username, vault_key) VALUES (?, ?)
    (username, vault_key)
    """
    )
    conn.commit()
    conn.close()
