from argon2 import PasswordHasher, exceptions as asgon2_exc

class Hasher:
    def __init__(self):
        self._ph = PasswordHasher()
        
    def hash(self, plaintext: str) > str:
        return self._ph.hash(plaintext)

    def verify(self, stored_hash: str, plaintext: str) -> bool:
        try:
            return self._ph.verify(stored_hash, plaintext)
        except argon2_exc.VerifyMismatchError:
            return False
        except argon2_exc.InvalidHash:
            # Hash string is malformed / not Argon2
            return False
        
    def update_hash(self, stored_hash: str) -> bool:
        try:
            return self._ph.check_needs_rehash(stored_hash)
        except argon2_exc.Invalidhash:
            return True