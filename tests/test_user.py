# tests/test_user.py
from src.user import User
from src.hasher import Hasher
from src.utils import derive_key
import base64


def test_user_from_plaintext_creates_valid_hash_and_salt():
    hasher = Hasher()
    email = "test@example.com"
    master_key = "MasterKey1!"

    user = User.from_plaintext(email, master_key, hasher)

    # Email should be set correctly
    assert user.email == email

    # Hash should verify with the same master key
    assert hasher.verify(user.vault_key_hash, master_key)

    # Salt should be a base64 string that decodes to 16 bytes
    salt_bytes = base64.b64decode(user.enc_salt)
    assert len(salt_bytes) == 16


def test_user_hash_fails_with_wrong_password():
    hasher = Hasher()
    email = "test@example.com"
    master_key = "MasterKey1!"

    user = User.from_plaintext(email, master_key, hasher)
    assert not hasher.verify(user.vault_key_hash, "WrongPassword")


def test_user_salt_changes_each_time():
    hasher = Hasher()
    u1 = User.from_plaintext("a@example.com", "MasterKey1!", hasher)
    u2 = User.from_plaintext("b@example.com", "MasterKey1!", hasher)

    assert u1.enc_salt != u2.enc_salt
