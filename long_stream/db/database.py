import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models.sentence import SentenceORM
from models.user import UserORM
from log import logger

DB_HOST = os.environ.get("LONG_STREAM_DB_HOST")
DB_PORT = os.environ.get("LONG_STREAM_DB_PORT")
DB_USER = os.environ.get("LONG_STREAM_DB_USER")
DB_PASSWORD = os.environ.get("LONG_STREAM_DB_PASSWORD")
DB_NAME = os.environ.get("LONG_STREAM_DB_NAME")
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)   # ← 提到全局

def init_db():
    orm_lists = [UserORM, SentenceORM]
    for orm in orm_lists:
        orm.__table__.create(bind=engine, checkfirst=True)
        logger.info(f"数据表 {orm.__tablename__} 结构已同步")

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()