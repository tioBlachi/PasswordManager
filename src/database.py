import sqlite3, os


class Database:
    def __init__(self, db_name: str = "passwords.db"):
        self.db_name = db_name

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self, db_name: str = "passwords.db"):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    vault_key TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def reset_db(self) -> None:
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
        return None

    def add_user(self, email: str, vault_key: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
            INSERT INTO users (email, vault_key) VALUES (?, ?)
            """,
                (email, vault_key),
            )
            conn.commit()
            return cur.lastrowid

    def get_user(self, email: str):
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,),
            )
            return cur.fetchone()
