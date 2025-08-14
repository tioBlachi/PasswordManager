# tests/test_utils.py
import base64
from src.utils import derive_key


def test_derive_key_is_deterministic():
    pw = "MasterKey1!"
    salt = base64.b64encode(b"fixed_salt_16byte").decode()  # 16 bytes
    k1 = derive_key(pw, salt)
    k2 = derive_key(pw, salt)
    assert isinstance(k1, bytes)
    assert k1 == k2


def test_derive_key_changes_with_salt():
    pw = "MasterKey1!"
    salt1 = base64.b64encode(b"fixed_salt_16byte").decode()
    salt2 = base64.b64encode(b"another_salt_16").decode()
    k1 = derive_key(pw, salt1)
    k2 = derive_key(pw, salt2)
    assert k1 != k2
