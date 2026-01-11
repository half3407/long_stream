# long_stream/utils/auth.py
import os
from sqlalchemy.orm import Session
from models.user import UserORM, UserOut
from utils.password import secret_hash_password, secret_verify_password
from db.database import get_db_session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
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