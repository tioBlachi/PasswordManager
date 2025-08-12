import pytest, os
from src import database as ut


def test_create_delete_db(db_name: str = "test_passwords.db"):
    db = ut.init_db(db_name)
    assert db is not None
    assert os.path.exists(db_name)
    db.close()
    ut.reset_db(db_name)
    assert not os.path.exists(db_name)


def test_add_user(db_name: str = "test_passwords.db"):
    ut.init_db(db_name)
    ut.add_user("test_user", "test_password", db_name)

    conn, cur = ut.get_db_connection(db_name)
    cur.execute("SELECT * FROM users WHERE username = ?", ("test_user",))
    user = cur.fetchone()

    assert user is not None
    assert user[1] == "test_user"
    assert user[2] == "test_password"
    ut.reset_db(db_name)
    conn.close()
    assert not os.path.exists(db_name)
