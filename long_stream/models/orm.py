from sqlalchemy import Column, Integer, String, DateTime, func
from long_stream.db.database import Base

class SentenceORM(Base):
    __tablename__ = "sentence"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(500), nullable=False)
    author = Column(String(100), nullable=False)
    source = Column(String(200))
    category = Column(String(50))
    create_at = Column(DateTime, server_default=func.now())
    update_at = Column(DateTime, onupdate=func.now())
    delete_at = Column(DateTime)

class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    account = Column(String(50), nullable=False)
    password_hash = Column(String(100), nullable=False)
    avatar = Column(String(255))
    create_at = Column(DateTime, server_default=func.now())
    update_at = Column(DateTime, onupdate=func.now())
    delete_at = Column(DateTime)