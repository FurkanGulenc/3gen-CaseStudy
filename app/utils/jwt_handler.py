from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

# Access Token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Refresh Token
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Token doğrulama
def verify_token(token: str, expected_type: str = "access"):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # sub claim'i kontrol et
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(
                status_code=401,
                detail="Token missing subject",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # type claim'i kontrol et
        token_type = payload.get("type")
        if token_type != expected_type:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token type. Expected {expected_type}.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
