import sqlite3
from typing import Optional, Tuple
from user import User
from hasher import Hasher
from database import Database
from vault import Vault
from getpass import getpass
from utils import *


def login(db: Database, hasher: Hasher) -> Optional[Tuple[User, str]]:
    print("==============================================")
    print("                   Login")
    print("==============================================\n")
    email = input("Enter Account Email: ").strip().lower()
    user = db.get_user(email)
    if not user:
        print("No account with that email")
        return None

    master_key = getpass("Enter Vault Password: \n")
    if user.verify(master_key, hasher):
        return user, master_key

    print("Invalid credentials")
    return None


def vault_loop(user: User, vault) -> None:
    while True:
        print("\n==============================================")
        print("                Lock Box Vault")
        print("==============================================\n")
        print("1. Store Password\n2. Manage Passwords\n3. Back\n")

        choice = input("Select an option (1-3): ").strip()
        if choice == "1":
            site = input("Enter website or app name: ").strip().capitalize()
            account = input("Enter username or email: ").strip()
            plain_pw = getpass("Enter password: ")
            vault.add_item(user.id, site, account, plain_pw)
            print("Saved.")
        elif choice == "2":  # Retrieve
            sites = list(vault.list_sites(user.id))
            if not sites:
                print("No sites found.")
                continue

            print("\nStored sites:")
            for idx, site in enumerate(sites, 1):
                print(f"{idx}. {site}")

            try:
                site_idx = int(input("Select a site by number: "))
                if site_idx < 1 or site_idx > len(sites):
                    print("Invalid site selection.")
                    continue
            except ValueError:
                print("Invalid input.")
                continue

            site_name = sites[site_idx - 1]
            items = vault.list_items_for_site(user.id, site_name)
            if not items:
                print("No accounts found for that site.")
                continue

            print(f"\nAccounts for {site_name}:")
            for idx, item in enumerate(items, 1):
                print(f"{idx}. {item['account']}")

            try:
                item_idx = int(input("Select an account by number. Enter to go back "))
                if item_idx < 1 or item_idx > len(items):
                    print("Invalid account selection.")
                    continue
            except ValueError:
                print("Invalid input.")
                continue

            item = items[item_idx - 1]

            while True:
                print("\n=== Current Credential ===")
                print(f"Site:    {item['site']}")
                print(f"Account: {item['account']}")

                print("\n1. Show password")
                print("2. Update password")
                print("3. Rename site/account")
                print("4. Delete account")
                print("5. Back")
                sub = input("Select: ").strip()

                if sub == "1":
                    pw = vault.get_password_by_id(item["id"])
                    print(
                        f"\nPassword for {item['site']} (Account: {item['account']}): "
                    )
                    print(pw)
                elif sub == "2":
                    new_pw = getpass(
                        f"Enter new password for {item['site']} ({item['account']}): "
                    )
                    if vault.update_password(item["id"], new_pw):
                        print(
                            f"Password updated for {item['site']} ({item['account']})."
                        )
                    else:
                        print("Update failed.")

                elif sub == "3":
                    new_site = (
                        input(f"New site [{item['site']}]. Enter to skip:  ").strip()
                        or item["site"]
                    )
                    new_account = (
                        input(
                            f"New account [{item['account']}]. Enter to skip: "
                        ).strip()
                        or item["account"]
                    )

                    if new_site == item["site"] and new_account == item["account"]:
                        print("No changes made. Information is identical")

                    if vault.update_meta(item["id"], new_site, new_account):
                        item["site"] = new_site
                        item["account"] = new_account
                        print(
                            f"Renamed to {item['site']} (Account: {item['account']}).\n"
                        )
                    else:
                        print("Rename failed.")

                elif sub == "4":
                    confirm = input(
                        f"Type DELETE to remove {item['site']} ({item['account']}) permanently: "
                    ).strip()
                    if confirm == "DELETE":
                        if vault.delete_item(item["id"]):
                            print("Account deleted.")
                            break  # Exit back to site list
                        else:
                            print("Delete failed.")
                    else:
                        print("Cancelled")

                elif sub == "5":
                    break  # Back to main vault menu

                else:
                    print("Invalid selection.")

        elif choice == "3":
            break
        else:
            print("Invalid choice.")


def create_account(db: Database, hasher: Hasher):
    print("\n==============================================")
    print("                Create Account")
    print("==============================================\n")

    email = is_valid_email()
    master_pw = is_valid_pw()
    new_user = User.from_plaintext(email, master_pw, hasher)
    try:
        user_id = db.add_user(new_user)
        print(f"Account Created! Email: {email}")
    except sqlite3.IntegrityError:
        print("This email is already registered")


def main():
    db = Database()
    db.init_db()

    h = Hasher()

    while True:
        print("\n================================================")
        print("                    Lock Box")
        print("================================================\n")
        print("1. Log In\n2. Create Account\n3. Quit")

        choice = input("Enter a choice (1-3)\n").strip()

        match choice:
            case "1":
                res = login(db, h)
                if not res:
                    continue
                user, master_pw = res
                aes_key = derive_key(master_pw, user.enc_salt)
                vault = Vault(db, aes_key)
                vault_loop(user, vault)
            case "2":
                create_account(db, h)
            case "3":
                print("Goodbye!")
                break
            case _:
                print("Invalid choice")


if __name__ == "__main__":
    main()
