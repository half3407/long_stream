# models_user.py
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func


class UserIn(BaseModel):
    username: str
    password: str  # 明文，只活在内存


class UserOut(BaseModel):
    id: int
    username: str  # 返回时不含密码


class UserORM(declarative_base()):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    create_at = Column(DateTime, server_default=func.now(), nullable=False)


class Token(BaseModel):
    access_token: str
    token_type: str