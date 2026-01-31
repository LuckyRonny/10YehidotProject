"""SHA-256 hashing utilities for digests and hex output."""
import hashlib


class Hasha256:
    @staticmethod
    def get_hash(st):
        """Return SHA-256 digest (raw bytes) of encoded string."""
        result = hashlib.sha256(st.encode())
        return result.digest()

    @staticmethod
    def get_hash_hex(st):
        """Return SHA-256 hex string of encoded string."""
        result = hashlib.sha256(st.encode())
        return result.hexdigest()


def main():
    """Run hashing tests on a sample string."""
    # initializing string
    st = "hello my name is inigo montoya"
    print(Hasha256.get_hash(st))
    print(Hasha256.get_hash_hex(st))


if __name__ == "__main__":
    main()
