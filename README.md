# SafePass

**SafePass** is a CLI password manager written in Python, designed for users who value simplicity, security, and full control over their data.

Created for submission as coursework of _WM187 - Programming for CyberSec_. Imported from GitLab.

## Key Features

- **Strong Encryption**: PBKDF2-HMAC key derivation for secure, salted, and stretched encryption keys.

- **Local Storage**: Your credentials are stored in a local encrypted database file, making it easy to back up or transfer without relying on cloud services.

- **Secure Password Generation**: Automatically generates completely random, high-entropy passwords.

- **Lightweight CLI Interface**: Manage, view, and generate passwords directly from your terminal with simple commands.

## Installation

The installation methods for each OS are provided below. Note that creating virtual environments is not mandatory.

On Windows:
```powershell
git clone https://git-lab.cyber.warwick.ac.uk/p4cs/SafePass.git
cd SafePass
python -m venv ./venv
.\venv\Scripts\activate
python -m pip install -e .
```

On Linux/MacOS:
```bash
git clone https://git-lab.cyber.warwick.ac.uk/p4cs/SafePass.git
cd SafePass
python3 -m venv ./venv
source ./venv/bin/activate
python -m pip install -e .
```

## Usage

Safepass provides an interactive interface, so simply run:

```
$ (venv) safepass
```
