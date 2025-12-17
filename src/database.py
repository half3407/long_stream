from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/sentence_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SentenceORM(Base):
    __tablename__ = "sentence"
    id      = Column(Integer, primary_key=True, index=True)
    content = Column(String(500), nullable=False)
    author  = Column(String(100), nullable=False)
    