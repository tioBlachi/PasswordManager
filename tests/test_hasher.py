from src.hasher import Hasher


def test_hasher():
    h = Hasher()
    digest = h.hash("secret_password")
    assert h.verify(digest, "secret_password")
    assert not h.verify(digest, "wrong")
