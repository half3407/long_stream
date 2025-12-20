from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models.sentence import SentenceORM
from models.user import UserORM
from log import logger

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/sentence_db"
SQL_BASE_MODULE = declarative_base()


def init_db():
    global SessionLocal
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    # ① 创建用户表（如果不存在）
    orm_lists = [UserORM, SentenceORM]

    for orm in orm_lists:
        orm.__table__.create(bind=engine, checkfirst=True)
        logger.info(f"数据表 {orm.__tablename__} 结构已同步")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 数据库会话依赖注入
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
