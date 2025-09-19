import hashlib, os

def hash_password(password: str, salt: str = None):
    if not salt:
        salt = os.urandom(16).hex()  # 16 byte random salt

    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed, salt

def verify_password(password: str, stored_hash: str, salt: str):
    hashed, _ = hash_password(password, salt)
    return hashed == stored_hash
