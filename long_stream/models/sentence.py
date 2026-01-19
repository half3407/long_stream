from datetime import datetime
from typing import Optional
from unittest.mock import Base
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base


# 2. 定义“句子”长什么样（字段、类型）
#    BaseModel 会自动把前端 JSON 变成 Python 对象，反之亦然。
class SentenceIn(BaseModel):
    content: str  # 只保留最刚需的字段，别的以后加
    author: str
    source: Optional[str] = None
    category: Optional[str] = None

class SentenceOut(BaseModel):
    id: int  # 返回时多带一个 id，让前端知道存哪了
    content: str
    author: str
    author: str
    source: Optional[str] = None
    category: Optional[str] = None
    create_at: datetime
    update_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
