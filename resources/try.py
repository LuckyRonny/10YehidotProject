from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# Generate a random 128-bit key
key = get_random_bytes(16)

# Generate a random 128-bit Initialization Vector (IV)
iv = get_random_bytes(16)

# Message to encrypt
message = b"This is a secret message."

# Create an AES cipher object in CBC mode
cipher = AES.new(key, AES.MODE_CBC, iv)

# Encrypt the message (padding is handled by pad function)
ciphertext = cipher.encrypt(pad(message, AES.block_size))

print(f"Original message: {message}")
print(f"Ciphertext: {ciphertext}")

# Decrypt the message
decipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = unpad(decipher.decrypt(ciphertext), AES.block_size)

print(f"Decrypted message: {plaintext}")
