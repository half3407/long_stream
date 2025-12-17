# main.py
# 0. 安装依赖（一次性）：
#    pip install fastapi uvicorn
from fastapi import Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal, SentenceORM
SentenceORM.__table__.create(bind=engine, checkfirst=True)
import datetime
from email.policy import HTTP
from fastapi import FastAPI, HTTPException
from fastapi import status
import uvicorn   # 帮我们省掉手写 JSON 解析的麻烦
from sentence import SentenceIn, SentenceOut;

# 数据库会话依赖注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 生成 FastAPI 应用实例；app 这个名字别改，因为启动命令里用到了
app = FastAPI()

# ========== 增 ==========
@app.post("/sentences", response_model=SentenceOut)
def create_sentence(sentence: SentenceIn, db: Session = Depends(get_db)):
    new_orm = SentenceORM(content=sentence.content, author=sentence.author)
    db.add(new_orm)
    db.commit()
    db.refresh(new_orm)
    return SentenceOut(id=new_orm.id, content=new_orm.content, author=new_orm.author) # pyright: ignore[reportArgumentType]


# ========== 查单条 ==========
@app.get("/sentences/{sentence_id}", response_model=SentenceOut)
def read_sentence(sentence_id: int, db: Session = Depends(get_db)):
    orm = db.get(SentenceORM, sentence_id)
    if not orm:
        raise HTTPException(status_code=404, detail="句子不存在")
    return SentenceOut(id=orm.id, content=orm.content, author=orm.author) # pyright: ignore[reportArgumentType]


# ========== 列表 ==========
@app.get("/sentences", response_model=list[SentenceOut])
def list_sentences(db: Session = Depends(get_db)):
    orms = db.query(SentenceORM).all()
    return [SentenceOut(id=o.id, content=o.content, author=o.author) for o in orms] # pyright: ignore[reportArgumentType]


# ========== 改 ==========
@app.put("/sentences/{sentence_id}", response_model=SentenceOut)
def update_sentence(sentence_id: int, payload: SentenceIn, db: Session = Depends(get_db)):
    orm = db.get(SentenceORM, sentence_id)
    if not orm:
        raise HTTPException(status_code=404, detail="句子不存在")
    orm.content = payload.content # type: ignore
    orm.author  = payload.author # pyright: ignore[reportAttributeAccessIssue]
    db.commit()
    db.refresh(orm)
    return SentenceOut(id=orm.id, content=orm.content, author=orm.author) # pyright: ignore[reportArgumentType]


# ========== 删 ==========
@app.delete("/sentences/{sentence_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sentence(sentence_id: int, db: Session = Depends(get_db)):
    orm = db.get(SentenceORM, sentence_id)
    if not orm:
        raise HTTPException(status_code=404, detail="句子不存在")
    db.delete(orm)
    db.commit()

# 程序主入口
if __name__ == "__main__":
    # 初始化日志
    from long_stream.log import init_logger,logger
    # 以当前时间命名日志文件，避免覆盖旧日志
    init_logger(f"long_stream_{datetime.date.today()}.log")
    logger.info("应用启动中...")
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
    )