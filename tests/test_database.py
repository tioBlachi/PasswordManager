import os
from src.database import Database
from src.user import User
from src.hasher import Hasher


def test_create_delete_db(tmp_path: str = "test_passwords.db"):
    db = Database(str(tmp_path))

    db.init_db()
    assert os.path.exists(db.db_name)

    db.reset_db()
    assert not os.path.exists(db.db_name)


def test_add_and_get_user(tmp_path: str = "test_passwords.db"):
    db = Database(tmp_path)
    db.init_db()

    hasher = Hasher()
    user = User.from_plaintext("test@email.com", "masterpw", hasher)
    new_id = db.add_user(user)
    assert new_id == user.id

    db_user = db.get_user("test@email.com")
    assert db_user is not None
    assert db_user.id == user.id
    assert db_user.email == user.email
    assert db_user.vault_key_hash != "masterpw"  # make sure stored pw is not plaintext
