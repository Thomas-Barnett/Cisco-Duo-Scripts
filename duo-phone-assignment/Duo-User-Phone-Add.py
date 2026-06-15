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


def get_target_users(admin_api):
    group_selector = os.getenv("DUO_GROUP")
    groups = None

    if not group_selector:
        groups = list(admin_api.get_groups_generator())

        print()
        print("Available Duo groups")
        for group in sorted(groups, key=lambda item: item["name"].casefold()):
            print(f"  - {group['name']} ({group['group_id']})")
        print("  - ALL (every Duo user)")
        print()

        group_selector = input("Enter the target Duo group name, group ID, or ALL: ").strip()

    if not group_selector:
        print("ERROR: A target Duo group is required. Use ALL to target every Duo user.")
        sys.exit(1)

    if group_selector.upper() == "ALL":
        return "ALL Duo users", list(admin_api.get_users_iterator())

    if groups is None:
        groups = list(admin_api.get_groups_generator())

    matches = [
        group for group in groups
        if group["group_id"] == group_selector
        or group["name"].casefold() == group_selector.casefold()
    ]

    if not matches:
        print(f"ERROR: Duo group not found: {group_selector}")
        print("Available Duo groups:")
        for group in sorted(groups, key=lambda item: item["name"].casefold()):
            print(f"  - {group['name']} ({group['group_id']})")
        sys.exit(1)

    if len(matches) > 1:
        print(f"ERROR: Multiple Duo groups are named: {group_selector}")
        print("Set DUO_GROUP to the desired group ID instead:")
        for group in matches:
            print(f"  - {group['name']} ({group['group_id']})")
        sys.exit(1)

    group = matches[0]
    users = list(admin_api.get_group_users_iterator(group["group_id"]))
    return f"{group['name']} ({group['group_id']})", users


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
    target_name, users = get_target_users(admin_api)
    print(f"Found {len(users)} users in target: {target_name}")

    phone = get_or_create_phone(admin_api, phone_number)
    phone_id = phone["phone_id"]

    existing_user_ids = {
        user["user_id"]
        for user in phone.get("users", [])
    }
    target_user_ids = {
        user["user_id"]
        for user in users
    }
    already_assigned_count = len(existing_user_ids & target_user_ids)

    users_to_update = [
        user for user in users
        if user["user_id"] not in existing_user_ids
    ]

    print()
    print("Planned changes")
    print(f"Phone number:         {phone_number}")
    print(f"Target:               {target_name}")
    print(f"Users in target:      {len(users)}")
    print(f"Already assigned:     {already_assigned_count}")
    print(f"Will be assigned:     {len(users_to_update)}")
    print()

    if not users_to_update:
        print("Nothing to do. Every user in the target already has this phone.")
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
