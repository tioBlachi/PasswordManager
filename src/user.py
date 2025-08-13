import os, base64


class User:
    def __init__(
        self, email: str, vault_key_hash: str, enc_salt: str, id: int | None = None
    ):
        self.id = id
        self.email = email.strip().lower()
        self.vault_key_hash = vault_key_hash
        self.enc_salt = enc_salt

    @classmethod
    def from_plaintext(
        cls, email: str, vault_key: str, hasher, salt_bytes: bytes | None = None
    ):
        """Create a User from a plaintext master password.
        - Hashes the master password (for login verification).
        - Generates (or uses provided) encryption salt for deriving the AES key.
        """
        if salt_bytes is None:
            salt_bytes = os.urandom(16)  # 128-bit random salt
        enc_salt_b64 = base64.b64encode(salt_bytes).decode()
        vault_key_hash = hasher.hash(vault_key)
        return cls(email.strip().lower(), vault_key_hash, enc_salt_b64)

    def verify(self, vault_key: str, hasher) -> bool:
        """Check if a provided vault key matches the stored hash."""
        return hasher.verify(self.vault_key_hash, vault_key)

    def get_enc_salt(self):
        return base64.b64decode(self.enc_salt)

    def __repr__(self):
        return f"User(id={self.id}, email='{self.email}')"
