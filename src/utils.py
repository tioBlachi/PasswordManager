import re

email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
password_pattern = (
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)


def is_valid_email() -> str:
    while True:
        email = input("Enter an Account Email: ")
        if re.fullmatch(email_regex, email):
            return email
        else:
            print("Invalid Email Format")


def is_valid_pw() -> str:
    while True:
        password = input("Enter Master Password: ")
        errors = []
        if len(password) < 8:
            errors.append("at least 8 characters long")
        if not re.search(r"[a-z]", password):
            errors.append("a lowercase letter")
        if not re.search(r"[A-Z]", password):
            errors.append("an uppercase letter")
        if not re.search(r"\d", password):
            errors.append("a digit")
        if not re.search(r"[@$!%*?&]", password):
            errors.append("a special character (@$!%*?&)")

        if errors:
            print("Password must contain: " + ", ".join(errors))
            continue
        return password
