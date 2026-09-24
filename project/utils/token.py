import hashlib

def generate_token(user_id: int, expire_date: str, secret_key: str) -> str:
    token_str = f"{user_id}:{expire_date}:{secret_key}"
    return hashlib.md5(token_str.encode()).hexdigest()
