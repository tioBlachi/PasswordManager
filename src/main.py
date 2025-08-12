import sqlite3
from user import User
from hasher import Hasher
from database import Database


def login():
    print("Login")


def create_account(db: Database, hasher: Hasher):
    print("==============\n" "Create Account\n" "==============\n")
    email = input("Enter an Account Email: ")
    master_pw = input("Enter Master Password: ")
    new_user = User.from_plaintext(email, master_pw, hasher)
    try:
        user_id = db.add_user(new_user)
        print(f"Account Created! User id: {user_id}")
    except sqlite3.IntegrityError:
        print("This email is already registered")


def quit_app():
    print("Quit")


def main():
    db = Database()
    db.init_db()

    h = Hasher()

    # user = User.from_plaintext("test@email.com", "masterkey", h)
    # user_id = db.add_user(user)

    # 1. User creates account
    print("================================================")
    print("                    Lock Box")
    print("================================================\n")
    print("1. Log In\n2. Create Account\n3. Quit")

    while True:
        choice = input("Enter a choice (1-3)\n").strip()

        match choice:
            case "1":
                login()
                break
            case "2":
                create_account(db, h)
                print("Redirecting to Login")
                db.list_users()
            case "3":
                quit_app()
                break
            case _:
                print("Invalid choice")

    # db.reset_db()


if __name__ == "__main__":
    main()
