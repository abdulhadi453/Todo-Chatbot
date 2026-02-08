"""
Cryptographic and security-related utilities.
These utilities provide secure cryptographic operations and security functions.
"""

import hashlib
import secrets
import hmac
from typing import Union, Optional
from datetime import datetime, timedelta
import base64
import bcrypt


class CryptoUtils:
    """
    Utility class for cryptographic and security-related operations.
    Provides secure functions for hashing, encryption, and other security measures.
    """

    @staticmethod
    def hash_password(password: str, salt_rounds: int = 12) -> tuple[str, str]:
        """
        Hash a password securely using bcrypt.

        Args:
            password: Plain text password to hash
            salt_rounds: Number of salt rounds for bcrypt (higher is more secure but slower)

        Returns:
            Tuple of (hashed_password, salt)
        """
        # Generate a salt and hash the password
        salt = bcrypt.gensalt(rounds=salt_rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Return as strings for storage
        return hashed.decode('utf-8'), salt.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password to verify
            hashed_password: Stored hashed password

        Returns:
            True if password matches the hash, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Generate a cryptographically secure random token.

        Args:
            length: Length of the token in bytes (default 32 bytes = 256 bits)

        Returns:
            Secure random token as a URL-safe string
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_verification_code(length: int = 6) -> str:
        """
        Generate a numeric verification code.

        Args:
            length: Length of the code (default 6 digits)

        Returns:
            Numeric verification code as a string
        """
        # Ensure length is reasonable
        length = max(1, min(length, 10))  # Limit between 1 and 10 digits

        # Generate random number with specified number of digits
        code = "".join([str(secrets.randbelow(10)) for _ in range(length)])
        return code

    @staticmethod
    def create_hmac_signature(message: str, secret_key: str) -> str:
        """
        Create an HMAC signature for a message.

        Args:
            message: Message to sign
            secret_key: Secret key to use for signing

        Returns:
            HMAC signature as hexadecimal string
        """
        # Create HMAC signature
        signature = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        return signature.hexdigest()

    @staticmethod
    def verify_hmac_signature(message: str, signature: str, secret_key: str) -> bool:
        """
        Verify an HMAC signature.

        Args:
            message: Original message
            signature: Signature to verify
            secret_key: Secret key used for signing

        Returns:
            True if signature is valid, False otherwise
        """
        expected_signature = CryptoUtils.create_hmac_signature(message, secret_key)
        return hmac.compare_digest(expected_signature, signature)

    @staticmethod
    def encrypt_simple(text: str, key: str) -> str:
        """
        Simple encryption using XOR with a key (for demonstration purposes only).
        Note: This is not secure for production use - use proper encryption libraries.

        Args:
            text: Text to encrypt
            key: Encryption key

        Returns:
            Base64-encoded encrypted text
        """
        # Pad key to match text length
        padded_key = (key * ((len(text) // len(key)) + 1))[:len(text)]

        # XOR operation
        encrypted_chars = [
            chr(ord(text_char) ^ ord(key_char))
            for text_char, key_char in zip(text, padded_key)
        ]

        # Encode as base64 for safe storage/transmission
        encrypted_text = ''.join(encrypted_chars)
        return base64.b64encode(encrypted_text.encode()).decode()

    @staticmethod
    def decrypt_simple(encrypted_text: str, key: str) -> str:
        """
        Simple decryption using XOR with a key (for demonstration purposes only).
        Note: This is not secure for production use - use proper encryption libraries.

        Args:
            encrypted_text: Base64-encoded encrypted text
            key: Decryption key

        Returns:
            Decrypted text
        """
        # Decode from base64
        encrypted_text = base64.b64decode(encrypted_text.encode()).decode()

        # Pad key to match text length
        padded_key = (key * ((len(encrypted_text) // len(key)) + 1))[:len(encrypted_text)]

        # XOR operation (same as encryption for XOR)
        decrypted_chars = [
            chr(ord(encrypted_char) ^ ord(key_char))
            for encrypted_char, key_char in zip(encrypted_text, padded_key)
        ]

        return ''.join(decrypted_chars)

    @staticmethod
    def hash_data(data: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """
        Hash arbitrary data using the specified algorithm.

        Args:
            data: Data to hash (string or bytes)
            algorithm: Hash algorithm to use (sha256, sha1, md5, etc.)

        Returns:
            Hexadecimal representation of the hash
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        hash_func = hashlib.new(algorithm)
        hash_func.update(data)
        return hash_func.hexdigest()

    @staticmethod
    def generate_salt(length: int = 32) -> str:
        """
        Generate a random salt.

        Args:
            length: Length of salt in bytes (default 32 bytes)

        Returns:
            Random salt as a hexadecimal string
        """
        return secrets.token_hex(length)

    @staticmethod
    def pbkdf2_hash(password: str, salt: str, iterations: int = 100000, key_length: int = 32) -> str:
        """
        Create a PBKDF2 hash of a password.

        Args:
            password: Password to hash
            salt: Salt to use
            iterations: Number of iterations (default 100,000)
            key_length: Length of the derived key in bytes (default 32)

        Returns:
            PBKDF2 hash as a hexadecimal string
        """
        derived_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations,
            key_length
        )
        return derived_key.hex()

    @staticmethod
    def mask_sensitive_data(data: str, visible_chars: int = 2, mask_char: str = '*') -> str:
        """
        Mask sensitive data like credit cards or SSNs.

        Args:
            data: Sensitive data to mask
            visible_chars: Number of characters to keep visible at the end
            mask_char: Character to use for masking

        Returns:
            Masked version of the data
        """
        if len(data) <= visible_chars:
            return mask_char * len(data)

        visible_part = data[-visible_chars:]
        masked_part = mask_char * (len(data) - visible_chars)

        return masked_part + visible_part

    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a secure API key.

        Returns:
            Randomly generated API key as a URL-safe string
        """
        # Generate a 64-character (512-bit) secure token
        return secrets.token_urlsafe(48)[:64]  # 48 bytes = 64 characters in URL-safe base64

    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """
        Validate the format of an API key.

        Args:
            api_key: API key to validate

        Returns:
            True if API key format is valid, False otherwise
        """
        if not isinstance(api_key, str):
            return False

        # Basic format validation - API keys should be 64 characters of base64url characters
        if len(api_key) != 64:
            return False

        # Check that it contains only URL-safe base64 characters
        import re
        pattern = r'^[A-Za-z0-9_-]+$'
        return bool(re.match(pattern, api_key))

    @staticmethod
    def hash_file(file_path: str, algorithm: str = 'sha256') -> str:
        """
        Hash the contents of a file.

        Args:
            file_path: Path to the file to hash
            algorithm: Hash algorithm to use

        Returns:
            Hexadecimal representation of the file hash
        """
        hash_func = hashlib.new(algorithm)

        with open(file_path, 'rb') as f:
            # Read file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)

        return hash_func.hexdigest()

    @staticmethod
    def generate_csrf_token() -> str:
        """
        Generate a CSRF token for form protection.

        Returns:
            Randomly generated CSRF token as a URL-safe string
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def constant_time_compare(a: str, b: str) -> bool:
        """
        Compare two strings in constant time to prevent timing attacks.

        Args:
            a: First string to compare
            b: Second string to compare

        Returns:
            True if strings are equal, False otherwise
        """
        return secrets.compare_digest(a, b)

    @staticmethod
    def validate_password_complexity(
        password: str,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digits: bool = True,
        require_special: bool = False
    ) -> tuple[bool, list[str]]:
        """
        Validate password complexity requirements.

        Args:
            password: Password to validate
            min_length: Minimum length requirement
            require_uppercase: Whether uppercase letters are required
            require_lowercase: Whether lowercase letters are required
            require_digits: Whether digits are required
            require_special: Whether special characters are required

        Returns:
            Tuple of (is_valid, list_of_requirement_failures)
        """
        failures = []

        if len(password) < min_length:
            failures.append(f"Password must be at least {min_length} characters")

        if require_uppercase and not any(c.isupper() for c in password):
            failures.append("Password must contain at least one uppercase letter")

        if require_lowercase and not any(c.islower() for c in password):
            failures.append("Password must contain at least one lowercase letter")

        if require_digits and not any(c.isdigit() for c in password):
            failures.append("Password must contain at least one digit")

        if require_special and not any(not c.isalnum() for c in password):
            failures.append("Password must contain at least one special character")

        return len(failures) == 0, failures