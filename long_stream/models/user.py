# models_user.py
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func
from typing import Optional


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