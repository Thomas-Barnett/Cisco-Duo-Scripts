# Add Shared Phone to Duo Users

This script uses the Duo Admin API to add one phone number to Duo user accounts.

It is safe to run multiple times. If a user already has the phone number assigned, the script skips that user.

## What It Does

The script will:

1. Connect to Duo using a Duo Admin API application
2. Read Duo users
3. Look up the phone number in Duo
4. Create the phone if it does not already exist
5. Assign the phone to users who do not already have it
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
```

Use E.164 format for the phone number:

```text
+19105551234
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
Found 42 Duo users.
Found existing Duo phone: +19105551234

Planned changes
Phone number:         +19105551234
Total Duo users:      42
Already assigned:     5
Will be assigned:     37

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
