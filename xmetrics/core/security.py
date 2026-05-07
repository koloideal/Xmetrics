from passlib.context import CryptContext

_crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _crypt.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _crypt.verify(plain, hashed)
