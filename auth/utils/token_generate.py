import jwt
from datetime import datetime, timedelta

SECRET_KEY = "aboba"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2880 # 2 дня, на "проде" было бы меньше, удобно для тестинга

def create_access_token(data, expires_delta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
