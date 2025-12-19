import bcrypt


def secret_hash_password(plain_password: str) -> bytes:
    """Hash a plaintext password using bcrypt."""
    # Ensure the password is in bytes
    plain_bytes = plain_password.encode("utf-8")[:72]  # Truncate to 72 bytes
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password
    hashed = bcrypt.hashpw(plain_bytes, salt)
    return hashed


def secret_verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """Verify a plaintext password against the hashed password."""
    plain_bytes = plain_password.encode("utf-8")[:72]  # Truncate to 72 bytes
    return bcrypt.checkpw(plain_bytes, hashed_password)
