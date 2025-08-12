def main():
    # 1. User creates account
    print("================================")
    print("            Lock Box           ")
    print("================================\n")
    print("1. Log In\n2. Create Account\n3. Quit")

    while True:
        try:
            choice = input("Enter a choice (1-3)").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if choice == "1":
            # TODO: handle login
            pass
        elif choice == "2":
            # TODO: handle account creation
            pass
        elif choice == "3":
            break
        else:
            print("Please enter a valid choice (1,2,3)")

    # 2. User logs into their account

    # 3. User is able to add a website and password to their database

    # 4. User can display their saved password for a website

    # 5. Optional: Consider hashing the website names as well


if __name__ == "__main__":
    main()
