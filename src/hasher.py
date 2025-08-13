import argon2


class Hasher:
    def __init__(self):
        self._ph = argon2.PasswordHasher()

    def hash(self, plaintext: str) -> str:
        return self._ph.hash(plaintext)

    def verify(self, stored_hash: str, plaintext: str) -> bool:
        try:
            if self._ph.verify(stored_hash, plaintext):
                print("Master Key Verified. Vault unlocked")
                return True
        except:
            print("Unable to verify Master Key")
            return False

    def update_hash(self, stored_hash: str) -> bool:
        try:
            return self._ph.check_needs_rehash(stored_hash)
        except argon2.exceptions.Invalidhash:
            return True
