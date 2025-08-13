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
        print("1. Store Password\n2. Retrieve Password\n3. Back\n")

        choice = input("Select an option (1-3): ").strip()
        if choice == "1":
            site = input("Enter website or app name: ").strip().capitalize()
            account = input("Enter username or email: ").strip()
            plain_pw = getpass("Enter password: ")
            vault.add_item(user.id, site, account, plain_pw)
            print("Saved.")
        elif choice == "2":
            sites = vault.list_sites(user.id)  # I changed this to return a set
            sites = sorted(sites)

            if not sites:
                print("No stored sites.")
                continue

            # Pick site
            print("\nStored sites:")
            for index, site in enumerate(sites, 1):
                print(f"{index}. {site}")
            try:
                index = int(input("Choose a site number: ").strip())
                if not (1 <= index <= len(sites)):
                    print("Invalid selection.")
                    continue
            except ValueError:
                print("Enter a number.")
                continue

            selected_site = sites[index - 1]
            items = vault.list_items_for_site(user.id, selected_site)

            # If multiple accounts for that site, pick one
            if len(items) > 1:
                print(f"\nAccounts for {selected_site}:")
                for i, it in enumerate(items, 1):
                    print(f"{i}. {it['account']}")
                try:
                    j = int(input("Choose an account number: ").strip())
                    if not (1 <= j <= len(items)):
                        print("Invalid selection.")
                        continue
                except ValueError:
                    print("Enter a number.")
                    continue
                item = items[j - 1]
            else:
                item = items[0]

            try:
                password = vault.get_password_by_id(item["id"])
                print("\n=== Credential ===")
                print(f"Site/App:\t{item['site']}")
                print(f"Account:\t{item['account']}")
                print(f"Password:\t{password}")
            except ValueError as e:
                print(f"Error: {e}")
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
