# generate_config.py
# ------------------
# Creates a config.yaml for streamlit-authenticator (v0.4.x API)
# Prompts you for users, hashes passwords correctly, and writes a secure cookie key.

import re
import secrets
import getpass
from pathlib import Path

import yaml
import streamlit_authenticator as stauth


def prompt_int(msg, min_value=1, max_value=100):
    while True:
        try:
            n = int(input(msg))
            if not (min_value <= n <= max_value):
                raise ValueError
            return n
        except ValueError:
            print(f"Please enter a number between {min_value} and {max_value}.")


def prompt_username():
    """
    Allow lowercase letters, numbers, ., _, - (3–30 chars).
    """
    pattern = re.compile(r"^[a-z0-9._-]{3,30}$")
    while True:
        u = input("  Username (lowercase, 3–30 chars, a-z 0-9 . _ -): ").strip()
        if pattern.fullmatch(u):
            return u
        print("  Invalid username. Try again.")


def prompt_name():
    n = input("  Full name: ").strip()
    return n or "User"


def prompt_email():
    e = input("  Email (optional, press Enter to skip): ").strip()
    return e or None


def prompt_password():
    while True:
        p1 = getpass.getpass("  Password (min 8 chars): ")
        p2 = getpass.getpass("  Confirm password: ")
        if p1 != p2:
            print("  Passwords do not match. Try again.")
            continue
        if len(p1) < 8:
            print("  Use at least 8 characters.")
            continue
        return p1


def main():
    print("=== Streamlit Auth Config Generator ===")
    n = prompt_int("How many users do you want to add? ")

    users = []
    for i in range(n):
        print(f"\nUser {i+1}:")
        name = prompt_name()
        username = prompt_username()
        email = prompt_email()
        password = prompt_password()
        users.append(
            {"name": name, "username": username, "email": email, "password": password}
        )

    # Secure random secret key for the auth cookie
    secret_key = secrets.token_urlsafe(32)

    # Hash passwords using the new API (v0.4.x)
    hasher = stauth.Hasher()
    hashed_pw = hasher.hash([u["password"] for u in users])
    for u, h in zip(users, hashed_pw):
        u["password"] = h

    # Cookie settings
    cookie_name = input("\nCookie name [app_auth_cookie]: ").strip() or "app_auth_cookie"
    try:
        expiry_days = int(input("Cookie expiry days [30]: ").strip() or "30")
    except ValueError:
        expiry_days = 30

    # Build YAML structure
    config = {
        "credentials": {
            "usernames": {
                u["username"]: {
                    "name": u["name"],
                    **({"email": u["email"]} if u["email"] else {}),
                    "password": u["password"],
                }
                for u in users
            }
        },
        "cookie": {"name": cookie_name, "key": secret_key, "expiry_days": expiry_days},
        "preauthorized": {"emails": []},  # you can list emails here if you want
    }

    out_path = Path("config.yaml")
    with out_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)

    print(f"\n✅ Wrote {out_path.resolve()}")
    print("Keep this file secret (do NOT commit to public repos).")


if __name__ == "__main__":
    main()
