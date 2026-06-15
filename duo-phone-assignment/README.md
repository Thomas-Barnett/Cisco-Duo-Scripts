# Add Shared Phone to Duo Users

This script uses the Duo Admin API to add one phone number to the users in a
specified Duo group.

It is safe to run multiple times. If a user already has the phone number assigned, the script skips that user.

## What It Does

The script will:

1. Connect to Duo using a Duo Admin API application
2. Find the specified Duo group and read its users
3. Look up the phone number in Duo
4. Create the phone if it does not already exist
5. Assign the phone to users in the target group who do not already have it
6. Skip users who already have the phone
7. Print a summary

> **Warning:** This script can assign the same phone number to multiple Duo users. Only use this if shared MFA phone behavior is intentional.

## Requirements

* Python 3
* Duo Admin API application
* Duo Admin API permissions:

  * Grant resource - Read
  * Grant resource - Write

Do **not** use credentials from a Microsoft RDP application. This script requires credentials from a Duo **Admin API** application.

## Duo Admin Setup

1. Log in to the Duo Admin Panel:

   ```text
   https://admin.duosecurity.com
   ```

2. Navigate to **Applications → Application Catalog**

3. Search for **Admin API**

4. Select **Add**

5. Name the application something clear, such as:

   ```text
   Duo Shared Phone Assignment Script
   ```

6. Enable these permissions:

   ```text
   Grant resource - Read
   Grant resource - Write
   ```

7. Save the application.

8. Copy the following values:

   ```text
   Integration key
   Secret key
   API hostname
   ```

These values will be added to the local `.env` file.

### Warning

**Do not ever commit `.env` or `.venv/` to GitHub.**


## Setup

From inside the script folder:

```bash
cd duo-phone-assignment
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If `requirements.txt` does not exist yet:

```bash
python -m pip install duo-client python-dotenv
```

## Configure `.env`

Copy the example file:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
nano .env
```

Example:

```env
DUO_IKEY=DIXXXXXXXXXXXXXXXXXX
DUO_SKEY=your-admin-api-secret-key
DUO_HOST=api-xxxxxxxx.duosecurity.com
DUO_PHONE=+19105551234
# DUO_GROUP=Your Duo Group Name
```

Use E.164 format for the phone number:

```text
+19105551234
```

### Optional `DUO_GROUP` Variable

`DUO_GROUP` is optional. Leave it commented out or remove it when you want to
choose the target group each time the script runs:

```env
# DUO_GROUP=Your Duo Group Name
```

When `DUO_GROUP` is not configured, the script retrieves your available Duo
groups and displays them before asking which group should receive the phone:

```text
Available Duo groups
  - Executives (DGXXXXXXXXXXXXXXXXXX)
  - Help Desk (DGYYYYYYYYYYYYYYYYYY)
  - ALL (every Duo user)

Enter the target Duo group name, group ID, or ALL:
```

You may enter a displayed group name, its group ID, or `ALL`.

Set `DUO_GROUP` when you want the script to automatically target the same group
without displaying the selection prompt:

```env
DUO_GROUP=Help Desk
```

You can also use a group ID:

```env
DUO_GROUP=DGYYYYYYYYYYYYYYYYYY
```

To intentionally assign the phone to every Duo user, set:

```env
DUO_GROUP=ALL
```

## Run the Script

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Run the script:

```bash
python duo_phone_assignment.py
```

The script will show planned changes before applying them.

Example:

```text
Connecting to Duo...
Found 12 users in target: Help Desk (DGXXXXXXXXXXXXXXXXXX)
Found existing Duo phone: +19105551234

Planned changes
Phone number:         +19105551234
Target:               Help Desk (DGXXXXXXXXXXXXXXXXXX)
Users in target:      12
Already assigned:     5
Will be assigned:     7

Type YES to apply these changes:
```

To apply the changes, type:

```text
YES
```

Any other response cancels the operation.

## References

Duo Admin API:

```text
https://duo.com/docs/adminapi
```

Duo Python Client:

```text
https://github.com/duosecurity/duo_client_python
```
