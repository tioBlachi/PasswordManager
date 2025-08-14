# CLI Password Manager

## Overview
This project is a command-line password manager inspired by my cryptography coursework at the University of Florida. The goal was to create a secure vault for storing account credentials with a strong focus on modern encryption and hashing techniques. The application is currently CLI-based with plans to add a GUI in the future.

## Security Design
- **Master Password Protection:** The master password is hashed using **Argon2id**, winner of the 2015 Password Hashing Competition, which is resistant to GPU cracking.
- **Vault Entry Encryption:** Individual password entries are encrypted using **AES-GCM**, which provides both confidentiality and integrity protection.
- **Metadata Binding:** Each entry’s encryption includes additional authenticated data (AAD) containing the `site` and `account` fields, preventing tampering.

## Architecture
- **Database:** SQLite is used for secure local storage.
- **Schema:**
  - `users` table stores a unique salt and Argon2id hash for each master password.
  - `vault` table stores encrypted password entries, along with associated metadata (site, account) and encryption nonces.
- **Flow:**
  1. User creates an account — email format is validated using regex, and the master password must be at least 8 characters long, include at least 1 uppercase letter, 1 digit, and 1 special character. Strong passwords are highly recommended for the master password.
  2. User logs in with the master password → Argon2id derives the vault key.
  3. Vault entries are decrypted on-demand using AES-GCM.
  4. New or updated entries are encrypted before being written to the database.

## Containerization
This app is containerized using Docker to simplify deploymwnt and ensure consistent environments. This is a step I take to practice using Docker.

## Running With Docker
**Build the image:**
```bash
docker build -t password-manager .
# Run the container
docker run -it --rm password-manager
```

## Future Plans
- Implement a GUI
- Encrypt all metadata for enhanced privacy
- Add clipboard integration for copying passwords securely
- Will work on improving as time becomes available