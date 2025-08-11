import pytest
from src import utils as ut


def test_create_delete_db(db_name: str = "test_passwords.db"):
    db = ut.init_db(db_name)
    assert db is not None
    db.close()
    assert ut.reset_db(db_name) is None
