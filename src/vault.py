from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
import os, base64


def _b64e(b: bytes) -> str:
    return base64.b64encode(b).decode()


def _b64d(s: str) -> bytes:
    return base64.b64decode(s)


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

    def update_password(self, item_id: int, new_plain_pw: str) -> int:
        """Re-encrypt password with SAME AAD (site/account)."""
        row = self.db.get_vault_item(item_id)
        if not row:
            return 0
        d = dict(row)
        aad = f"{d['site']}:{d['account']}".encode()

        nonce = os.urandom(12)
        ct = self._aesgcm.encrypt(nonce, new_plain_pw.encode(), aad)
        return self.db.update_vault_item_cipher(item_id, _b64e(ct), _b64e(nonce))

    def update_meta(self, item_id: int, new_site: str, new_account: str) -> int:
        """
        Change site/account. Since AAD changes, we must:
        - decrypt with OLD AAD
        - re-encrypt with NEW AAD + new nonce
        - update cipher+nonce and then update site/account (order doesn’t matter if same txn; here two calls)
        """
        row = self.db.get_vault_item(item_id)
        if not row:
            return 0
        d = dict(row)

        # Decrypt with OLD AAD
        old_aad = f"{d['site']}:{d['account']}".encode()
        ct = _b64d(d["ciphertext"])
        nonce = _b64d(d["nonce"])
        plain_pw = self._aesgcm.decrypt(nonce, ct, old_aad).decode()

        # Re-encrypt with NEW AAD
        new_site_norm = new_site.strip()
        new_account_norm = new_account.strip()
        new_aad = f"{new_site_norm}:{new_account_norm}".encode()
        new_nonce = os.urandom(12)
        new_ct = self._aesgcm.encrypt(new_nonce, plain_pw.encode(), new_aad)

        # Persist
        self.db.update_vault_item_cipher(item_id, _b64e(new_ct), _b64e(new_nonce))
        return self.db.update_vault_item_meta(item_id, new_site_norm, new_account_norm)

    def delete_item(self, item_id: int) -> int:
        return self.db.delete_vault_item(item_id)
