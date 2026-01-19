from long_stream.db.database import engine, SessionLocal
from long_stream.models.orm import SentenceORM, UserORM

# 提供 get_db 依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()