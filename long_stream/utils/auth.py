# long_stream/utils/auth.py
import os
from fastapi import security
from sqlalchemy.orm import Session
from models import get_db
from models.orm import UserORM
from models.user import User, UserOut
from utils.password import secret_hash_password, secret_verify_password
from db.database import get_db_session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer, HTTPBearer
from jose import JWTError, jwt
from typing import Optional
from models.token import TokenData
from datetime import datetime, timedelta


def register_user(username: str, password: str, db: Session = Depends(get_db_session)) -> UserOut:
    # 1. 唯一性检查
    if db.query(UserORM).filter(UserORM.username == username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    # 2. 哈希入库
    new_user = UserORM(username=username, password_hash=secret_hash_password(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserOut(**new_user.__dict__)

def login_user(username: str, password: str, db: Session = Depends(get_db_session)) -> dict:
    user = db.query(UserORM).filter(UserORM.username == username).first()
    if not user or not secret_verify_password(password, user.password_hash): # type: ignore
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return {"id": user.id, "username": user.username}

SECRET_KEY: str = os.environ["SECRET_KEY"]
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")  # 默认 HS256
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
def verify_token(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if "sub" not in payload or "username" not in payload:
            raise HTTPException(status_code=401, detail="无效凭证")
        return TokenData(sub=payload["sub"], username=payload["username"])
    except Exception as e:
        print("JWT 解码错误:", str(e))
        raise HTTPException(status_code=401, detail="无效凭证")
    


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# 权限依赖：要求至少是普通用户
def require_user(current_user: UserORM = Depends(get_current_user)):
    if current_user.role not in ["user", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return current_user

# 权限依赖：要求是管理员
def require_admin(current_user: UserORM = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# 游客可访问（无需认证），但也可用于区分是否登录
def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(), use_cache=False),
    db: Session = Depends(get_db)
):
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        return db.query(UserORM).filter(UserORM.id == user_id).first() if user_id else None
    except:
        return None