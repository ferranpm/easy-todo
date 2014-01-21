from passlib.hash import sha256_crypt


def get_hash(raw_password):
    return sha256_crypt.encrypt(raw_password)

def verify_password(raw_password, hashed_password):
    return sha256_crypt.verify(raw_password, hashed_password)
