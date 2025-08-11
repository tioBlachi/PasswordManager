import pytest, sqlite3
from src import utils as ut


def test_create_delete_db(db_name: str = "test_passwords.db"):
    db = ut.init_db(db_name)
    assert db is not None
    db.close()
    assert ut.reset_db(db_name) is None


def test_add_user(db_name: str = "test_passwords.db"):
    ut.init_db(db_name)
    ut.add_user("test_user", "test_password", db_name)

    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", ("test_user",))
        user = cur.fetchone()

    assert user is not None
    assert user[1] == "test_user"
    assert user[2] == "test_password"
    ut.reset_db(db_name)
