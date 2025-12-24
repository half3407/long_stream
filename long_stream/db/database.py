from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from long_stream.models.sentence import SentenceORM
from long_stream.models.user import UserORM
from long_stream.log import logger

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/sentence_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)   # ← 提到全局

def init_db():
    orm_lists = [UserORM, SentenceORM]
    for orm in orm_lists:
        orm.__table__.create(bind=engine, checkfirst=True)
        logger.info(f"数据表 {orm.__tablename__} 结构已同步")

def get_db_session():
    db = SessionLocal()   # ← 现在一定能找到
    try:
        yield db
    finally:
        db.close()