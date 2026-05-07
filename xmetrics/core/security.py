import bcrypt

_MAX = 72


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode()[:_MAX], bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode()[:_MAX], hashed.encode())
