import sqlite3
import os
from src.user import User


class Database:
    def __init__(self, db_name: str = "passwords.db"):
        self.db_name = db_name

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    vault_key_hash TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def reset_db(self) -> None:
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
        return None

    def add_user(self, user: User) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
            INSERT INTO users (email, vault_key_hash) VALUES (?, ?)
            """,
                (user.email, user.vault_key_hash),
            )
            user.id = cur.lastrowid
            return user.id

    def get_user(self, email: str) -> User:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
            if not row:
                return None
            return User(
                email=row["email"], vault_key_hash=row["vault_key_hash"], id=row["id"]
            )

    def delete_user(self, email: str) -> int:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM users WHERE email = ?", (email,))
            return cur.rowcount

    def list_users(self) -> list[User]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM users ORDER BY id").fethcall()
            return [
                User(row["email"], row["vault_key_hash"], row["id"]) for row in rows
            ]
