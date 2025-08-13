from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptogrophy.exceptions import InvalidTag
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

    def list_items(self, user_id: int):
        items = self.db.get_vault_items(user_id)  # expect list of sqlite3.Row
        result = []
        for row in items:
            rowd = dict(row)  # convert Row -> dict for **unpacking
            pwd = self.decrypt_password(
                rowd["ciphertext"], rowd["nonce"], rowd["site"], rowd["account"]
            )
            result.append({**rowd, "password": pwd})
        return result

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
