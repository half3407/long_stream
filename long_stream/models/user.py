# models_user.py
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, func
from typing import Optional
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")  # 可选值: "guest", "user", "admin"


class UserIn(BaseModel):
    username: str
    password: str  # 明文，只活在内存
    account: str


class UserOut(BaseModel):
    id: int
    username: str  # 返回时不含密码
    account: str
    avatar: Optional[str] = None
    create_at: datetime
    update_at: Optional[datetime] = None
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str