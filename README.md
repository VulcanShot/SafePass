# SafePass

**SafePass** is a CLI password manager written in Python, designed for users who value simplicity, security, and full control over their data.

## Key Features

- **Strong Encryption**: PBKDF2-HMAC key derivation for secure, salted, and stretched encryption keys.

- **Local Storage**: Your credentials are stored in a local encrypted database file, making it easy to back up or transfer without relying on cloud services.

- **Secure Password Generation**: Automatically generates completely random, high-entropy passwords.

- **Lightweight CLI Interface**: Manage, view, and generate passwords directly from your terminal with simple commands.

## Installation

```
$ git clone https://git-lab.cyber.warwick.ac.uk/p4cs/SafePass.git
$ cd SafePass
$ pip install -e .
```

## Usage

Safepass provides a convinient CLI, so just run `safepass`.