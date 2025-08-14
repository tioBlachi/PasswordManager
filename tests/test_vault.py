# tests/test_vault.py
from src.database import Database
from src.user import User
from src.hasher import Hasher
from src.utils import derive_key
from src.vault import Vault


def test_vault_roundtrip(tmp_path):
    db_path = tmp_path / "passwords.db"
    db = Database(str(db_path))
    db.init_db()

    # Create user
    hasher = Hasher()
    user = User.from_plaintext("user@example.com", "MasterKey1!", hasher)
    user_id = db.add_user(user)

    # Derive session key (bytes) from plaintext + stored enc_salt
    key = derive_key("MasterKey1!", user.enc_salt)

    # Use Vault to add & fetch
    vault = Vault(db, key)
    site = "Netflix"
    account = "me@example.com"
    plaintext_pw = "Pa$$w0rd!"

    item_id = vault.add_item(user_id, site, account, plaintext_pw)
    assert isinstance(item_id, int)

    # Retrieve list for site and pick the item
    items = vault.list_items_for_site(user_id, site)
    assert len(items) == 1
    item = items[0]
    assert item["site"] == site
    assert item["account"] == account

    # Decrypt
    recovered = vault.get_password_by_id(item["id"])
    assert recovered == plaintext_pw
