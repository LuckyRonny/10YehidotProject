"""
Server-side AES encryption/decryption for secure channel.
"""
import base64
import hashlib

# install pycryptodome
from Crypto import Random
from Crypto.Cipher import AES

# Key generation: random bytes length and digest size for SHA256
KEY_RANDOM_BYTES = 32
NO_OVER = 1


class AESCipher(object):
    """AES CBC cipher for encrypting/decrypting message payloads."""

    @staticmethod
    def encrypt(key, raw):
        """Encrypt raw bytes with key
         returns base64-encoded iv + ciphertext."""
        raw = AESCipher._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        b = base64.b64encode(iv + cipher.encrypt(raw))
        return b

    @staticmethod
    def decrypt(key, enc):
        """Decrypt base64-encoded payload; returns raw bytes."""
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return AESCipher._unpad(cipher.decrypt(enc[AES.block_size:]))

    @staticmethod
    def _pad(s):
        """Pad input to AES block size using PKCS7-style padding."""
        bs = AES.block_size
        k = s + (bs - len(s) % bs) * chr(bs - len(s) % bs).encode()
        return k

    @staticmethod
    def _unpad(s):
        """Remove PKCS7-style padding from decrypted bytes."""
        return s[:-ord(s[len(s) - NO_OVER:])]

    @staticmethod
    def generate_key():
        """Generate a 256-bit key from random bytes hashed with SHA256."""
        key = Random.new().read(KEY_RANDOM_BYTES)
        key = hashlib.sha256(key).digest()
        return key
