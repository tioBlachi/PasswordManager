import os
from src.database import Database


def test_create_delete_db(tmp_path: str = "test_passwords.db"):
    db = Database(str(tmp_path))

    db.init_db()
    assert os.path.exists(db.db_name)

    db.reset_db()
    assert not os.path.exists(db.db_name)


def test_add_user_and_fetch(tmp_path: str = "test_passwords.db"):
    db = Database(str(tmp_path))
    db.init_db()

    email = "test@email.com"
    vault_key = "test_password"

    user_id = db.add_user(email, vault_key)
    assert isinstance(user_id, int)

    row = db.get_user(email)
    assert row is not None
    assert row["email"] == email
    assert row["vault_key"] == vault_key

    db.reset_db()
    assert not os.path.exists(db.db_name)
