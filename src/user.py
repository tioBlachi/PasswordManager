class User:
    def __init__(self, email: str, vault_key_hash: str, id: int | None = None):
        self.id = id
        self.email = email.strip().lower()
        self.vault_key_hash = vault_key_hash

    @classmethod
    def from_plaintext(cls, email: str, vault_key: str, hasher):
        """Factory that hashes the vault key immediately."""
        return cls(email.strip().lower(), hasher.hash(vault_key))

    def verify(self, vault_key: str, hasher) -> bool:
        """Check if a provided vault key matches the stored hash."""
        return hasher.verify(self.vault_key_hash, vault_key)

    def __repr__(self):
        return f"User(id={self.id}, email='{self.email}')"
