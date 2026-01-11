from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import UserIn, UserORM, UserOut
from db.database import get_db_session
from utils.password import generate_jwt, secret_hash_password, secret_verify_password
from models.user import Token
from utils.password import generate_user_jwt

user_router = APIRouter(prefix="", tags=["用户认证"])


@user_router.post("/register", response_model=UserOut)
def register(user: UserIn, db: Session = Depends(get_db_session)):
    """
    1. 检查用户名重复
    2. 密码哈希
    3. 入库
    4. 返回不含密码的用户信息
    """
    # ① 唯一性检查
    if db.query(UserORM).filter(UserORM.username == user.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # ③ 入库
    new_user = UserORM(
        username=user.username, password_hash=secret_hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # ④ 返回（不含密码）
    return UserOut(**new_user.__dict__)

@user_router.post("/login", response_model=Token, tags=["用户认证"])
def login(form: UserIn, db: Session = Depends(get_db_session)):
    user = db.query(UserORM).filter(UserORM.username == form.username).first()
    if not user or not secret_verify_password(form.password, user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token_data = {
        "sub": str(user.id), 
        "username": user.username,
    }
    access_token = generate_jwt(token_data, exp_minutes=30)
    return {"access_token": access_token, "token_type": "bearer"}