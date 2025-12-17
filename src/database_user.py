from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base

class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, index = True)
    username = Column(String(50), unique = True, index = True, nullable = False)
    password_hash = Column(String(100), nullable = False)
    create_at = Column(DateTime, server_default=func.now(), nullable = False)
    