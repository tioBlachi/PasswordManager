from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os, base64


class Vault:
    def __init__(self, db, aes_key: bytes):
        self.db = db
        self.aes_key = aes_key

    def add_item(self, user_id, site, account, password_plain):
        nonce = os.urandom(12)
        aesgcm = AESGCM(self.aes_key)
        ciphertext = aesgcm.encrypt(nonce, password_plain.encode(), None)

        self.db.add_vault_item(
            user_id,
            site,
            account,
            base64.b64encode(ciphertext).decode(),
            base64.b64encode(nonce).decode(),
        )

    def list_items(self, user_id):
        items = self.db.get_vault_items(user_id)
        result = []
        for item in items:
            password = self.decrypt_password(item["ciphertext"], item["nonce"])
            result.append({**item, "password": password})
        return result

    def decrypt_password(self, ciphertext_b64, nonce_b64):
        aesgcm = AESGCM(self.aes_key)
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
        return aesgcm.decrypt(nonce, ciphertext, None).decode()
