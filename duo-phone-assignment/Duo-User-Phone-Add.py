import os
import sys
from getpass import getpass
from pathlib import Path

try:
    import duo_client
except ModuleNotFoundError as error:
    if error.name != "duo_client":
        raise
    print(
        "ERROR: The duo_client package is not installed for this Python interpreter.\n"
        "Activate .venv or run: python -m pip install -r requirements.txt"
    )
    sys.exit(1)

from dotenv import load_dotenv


load_dotenv(dotenv_path=Path(__file__).with_name(".env"))


def required_env(name, prompt_secret=False):
    value = os.getenv(name)
    if value:
        return value

    if prompt_secret:
        value = getpass(f"Enter {name} (input hidden): ").strip()
        if value:
            return value

    print(f"ERROR: Missing required environment value: {name}")
    sys.exit(1)


DUO_IKEY = required_env("DUO_IKEY")
DUO_SKEY = required_env("DUO_SKEY", prompt_secret=True)
DUO_HOST = required_env("DUO_HOST")


def normalize_phone_number(phone_number):
    cleaned = phone_number.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    if not cleaned.startswith("+"):
        print("ERROR: Phone number must be in E.164 format, for example: +19105551234")
        sys.exit(1)

    return cleaned


def get_or_create_phone(admin_api, phone_number):
    phones = admin_api.get_phones_by_number(phone_number)

    if phones:
        phone = phones[0]
        print(f"Found existing Duo phone: {phone_number}")
        return phone

    print(f"No existing Duo phone found for {phone_number}")

    phone = admin_api.add_phone(
        number=phone_number,
        name="Shared Phone",
        type="Mobile",
        platform="Generic Smartphone",
    )

    print(f"Created Duo phone: {phone_number}")
    return phone


def main():
    phone_number = os.getenv("DUO_PHONE")

    if not phone_number:
        phone_number = input("Enter phone number in E.164 format, example +19105551234: ")

    phone_number = normalize_phone_number(phone_number)

    admin_api = duo_client.Admin(
        ikey=DUO_IKEY,
        skey=DUO_SKEY,
        host=DUO_HOST,
    )

    print("Connecting to Duo...")
    users = admin_api.get_users()
    print(f"Found {len(users)} Duo users.")

    phone = get_or_create_phone(admin_api, phone_number)
    phone_id = phone["phone_id"]

    existing_user_ids = {
        user["user_id"]
        for user in phone.get("users", [])
    }

    users_to_update = [
        user for user in users
        if user["user_id"] not in existing_user_ids
    ]

    print()
    print("Planned changes")
    print(f"Phone number:         {phone_number}")
    print(f"Total Duo users:      {len(users)}")
    print(f"Already assigned:     {len(existing_user_ids)}")
    print(f"Will be assigned:     {len(users_to_update)}")
    print()

    if not users_to_update:
        print("Nothing to do. Every user already has this phone.")
        return

    confirm = input("Type YES to apply these changes: ")

    if confirm != "YES":
        print("Canceled. No changes were made.")
        return

    added = 0
    failed = 0

    for user in users_to_update:
        username = user["username"]
        user_id = user["user_id"]

        try:
            admin_api.add_user_phone(user_id, phone_id)
            print(f"ADDED: {phone_number} to {username}")
            added += 1
        except Exception as error:
            print(f"FAILED: {username}: {error}")
            failed += 1

    print()
    print("Summary")
    print(f"Added:  {added}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
