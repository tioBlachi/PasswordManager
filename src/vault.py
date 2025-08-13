from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
import os, base64


class Vault:
    def __init__(self, db, master_key: bytes):
        self.db = db
        self.master_key = master_key
        self._aesgcm = AESGCM(master_key)

    def add_item(self, user_id, site, account, password_plain):
        nonce = os.urandom(12)
        aad = f"{site}:{account}".encode()
        ciphertext = self._aesgcm.encrypt(nonce, password_plain.encode(), aad)

        return self.db.add_vault_item(
            user_id,
            site,
            account.strip(),
            base64.b64encode(ciphertext).decode(),
            base64.b64encode(nonce).decode(),
        )

    def list_sites(self, user_id: int):
        return self.db.get_vault_sites(user_id)

    def decrypt_password(
        self,
        ciphertext_b64: str,
        nonce_b64: str,
        site: str | None = None,
        account: str | None = None,
    ) -> str:
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
        aad = f"{site}:{account}".encode() if site and account else None
        try:
            return self._aesgcm.decrypt(nonce, ciphertext, aad).decode()
        except InvalidTag:
            raise ValueError("Decryption failed")

    def list_items_for_site(self, user_id: int, site: str) -> list[dict]:
        rows = self.db.get_vault_items_for_site(user_id, site)
        return [dict(r) for r in rows]

    def get_password_by_id(self, item_id: int) -> str:
        row = self.db.get_vault_item(item_id)
        if not row:
            raise ValueError("Item not found")
        d = dict(row)
        # Use AAD binding with site:account
        return self.decrypt_password(
            d["ciphertext"], d["nonce"], d["site"], d["account"]
        )
