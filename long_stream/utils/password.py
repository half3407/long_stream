import os
import jwt
import bcrypt
from typing import Dict
from models.user import UserOut
from datetime import datetime, timedelta, timezone


def secret_hash_password(plain_password: str) -> bytes:
    """Hash a plaintext password using bcrypt."""
    # Ensure the password is in bytes
    plain_bytes = plain_password.encode("utf-8")[:72]  # Truncate to 72 bytes
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password
    hashed = bcrypt.hashpw(plain_bytes, salt)
    return hashed


def secret_verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """Verify a plaintext password against the hashed password."""
    plain_bytes = plain_password.encode("utf-8")[:72]  # Truncate to 72 bytes
    return bcrypt.checkpw(plain_bytes, hashed_password)


from jwt import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = os.environ.get("LONG_STREAM_JWT_SECRET")
ALGORITHM = "HS256"


# 生成 JWT
# def generate_jwt(user_id: str) -> str:
#     data_body = {
#         "sub": user_id,
#         "iat": datetime.utcnow(), # 签发时间
#         "exp": datetime.utcnow() + timedelta(hours=1), # 过期时间
#     }
#     return jwt.encode(data_body, SECRET_KEY, algorithm=ALGORITHM)
def generate_jwt(data_body: Dict, exp: datetime) -> str:
    data_body["iat"] = datetime.now(timezone.utc)
    data_body["exp"] = exp
    return jwt.encode(data_body, SECRET_KEY, algorithm=ALGORITHM)


def generate_user_jwt(user: UserOut) -> str:
    # FIXME: 这里的jwt没有缓存到数据库中，可能存在多用户同时登录的问题
    exp = datetime.now(timezone.utc) + timedelta(days=7)  # 有效期7天
    data_body = {
        "user_id": user.id,
        "user_username": user.username,
        "user_create_at": user.create_at,
    }
    return generate_jwt(data_body, exp)


# 校验 JWT(待优化)
def verify_jwt(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience="your-app",
            issuer="auth-server",
        )
        return payload
    except ExpiredSignatureError:
        return "Token 已过期"
    except InvalidTokenError:
        return "Token 无效"
