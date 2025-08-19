import os
import base64
import sqlite3
from src.database import Database
from src.user import User
from src.hasher import Hasher


def test_create_delete_db(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))

    db.init_db()
    assert db_path.exists()

    db.reset_db()
    assert not db_path.exists()


def test_users_table_has_enc_salt(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    db.init_db()

    with sqlite3.connect(str(db_path)) as conn:
        cols = [c[1] for c in conn.execute("PRAGMA table_info(users)").fetchall()]
    assert "enc_salt" in cols


def test_add_and_get_user(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    db.init_db()

    hasher = Hasher()
    user = User.from_plaintext("test@email.com", "masterpw", hasher)
    new_id = db.add_user(user)
    assert isinstance(new_id, int)
    assert new_id == user.id

    db_user = db.get_user("test@email.com")
    assert db_user is not None
    assert db_user.id == user.id
    assert db_user.email == user.email
    assert db_user.vault_key_hash != "masterpw"  # not storing plaintext


def test_vault_item_crud(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    db.init_db()

    # Create a user
    hasher = Hasher()
    user = User.from_plaintext("a@b.com", "pw", hasher)
    user_id = db.add_user(user)
    assert isinstance(user_id, int)

    # Add a vault item
    site = "Netflix"
    account = "me@example.com"
    ct1 = base64.b64encode(b"cipher1").decode()
    n1 = base64.b64encode(b"nonce1").decode()
    item_id = db.add_vault_item(user_id, site, account, ct1, n1)
    assert isinstance(item_id, int)

    # List sites (should include Netflix)
    sites = db.get_vault_sites(user_id)
    assert isinstance(sites, set)
    assert site in sites

    # Get items for site
    items = db.get_vault_items_for_site(user_id, site)
    assert len(items) == 1
    row = dict(items[0])
    assert row["id"] == item_id
    assert row["site"] == site
    assert row["account"] == account
    assert row["ciphertext"] == ct1
    assert row["nonce"] == n1

    # Update cipher only
    ct2 = base64.b64encode(b"cipher2").decode()
    n2 = base64.b64encode(b"nonce2").decode()
    changed = db.update_vault_item_cipher(item_id, ct2, n2)
    assert changed == 1

    fetched = db.get_vault_item(item_id)
    assert fetched is not None
    fetched_d = dict(fetched)
    assert fetched_d["ciphertext"] == ct2
    assert fetched_d["nonce"] == n2

    # Update metadata (site/account)
    new_site = "Hulu"
    new_account = "new@example.com"
    changed = db.update_vault_item_meta(item_id, new_site, new_account)
    assert changed == 1

    fetched2 = db.get_vault_item(item_id)
    fd2 = dict(fetched2)
    assert fd2["site"] == new_site
    assert fd2["account"] == new_account

    # Delete the item
    deleted = db.delete_vault_item(item_id)
    assert deleted == 1
    assert db.get_vault_item(item_id) is None
