import hashlib

def hash_url(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()