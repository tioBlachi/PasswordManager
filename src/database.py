import sqlite3
import os
from user import User


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
                    vault_key_hash TEXT NOT NULL,
                    enc_salt TEXT NOT NULL
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vault_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                site TEXT NOT NULL,
                account TEXT NOT NULL,
                ciphertext TEXT NOT NULL,
                nonce TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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
            INSERT INTO users (email, vault_key_hash, enc_salt) VALUES (?, ?, ?)
            """,
                (user.email, user.vault_key_hash, user.enc_salt),
            )
            user.id = cur.lastrowid
            return user.id

    def get_user(self, email: str) -> User:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT id, email, vault_key_hash, enc_salt FROM users WHERE email = ?",
                (email.strip().lower(),),
            )
            row = cur.fetchone()
            if row:
                return User(
                    id=row["id"],
                    email=row["email"],
                    vault_key_hash=row["vault_key_hash"],
                    enc_salt=row["enc_salt"],
                )
        return None

    def delete_user(self, email: str) -> int:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM users WHERE email = ?", (email,))
            return cur.rowcount

    def list_users(self) -> list[User]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
            return [
                User(row["email"], row["vault_key_hash"], row["id"]) for row in rows
            ]

    def add_vault_item(
        self,
        user_id: int,
        site: str,
        account: str,
        b64_ciphertext: str,
        b64_nonce: str,
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO vault_items (user_id, site, account, ciphertext, nonce)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, site.strip(), account.strip(), b64_ciphertext, b64_nonce),
            )
            return cur.lastrowid

    def get_vault_sites(self, user_id: int):
        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT site FROM vault_items WHERE user_id = ?
                """,
                (user_id,),
            )
            return set([row[0] for row in cur.fetchall()])

    def get_vault_item(self, item_id: int):
        with self._connect() as conn:
            return conn.execute(
                """
            SELECT id, user_id, site, account, ciphertext, nonce
            FROM vault_items
            WHERE id = ?
            """,
                (item_id,),
            ).fetchone()

    def get_vault_items_for_site(self, user_id: int, site: str):
        with self._connect() as conn:
            return conn.execute(
                """
            SELECT id, site, account, ciphertext, nonce
            FROM vault_items
            WHERE user_id = ? AND site = ?
            ORDER BY account
            """,
                (user_id, site.strip()),
            ).fetchall()
