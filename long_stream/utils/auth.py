# long_stream/utils/auth.py
from sqlalchemy.orm import Session
from models.user import UserORM, UserOut
from utils.password import secret_hash_password, secret_verify_password
from db.database import get_db_session
from fastapi import Depends, HTTPException

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