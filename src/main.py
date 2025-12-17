# main.py
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
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database_user import UserORM
from models_user import UserIn, UserOut

# 数据库会话依赖注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 生成 FastAPI 应用实例；app 这个名字别改，因为启动命令里用到了
app = FastAPI()

# ① 创建用户表（如果不存在）
UserORM.__table__.create(bind=engine, checkfirst=True)

# ② 密码哈希工具(使用原生 bcrypt，关闭 passlib 自检)
pwd_ctx = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12,   # 可选：哈希强度
    # 关键：跳过内部检测，避免触发 >72 字节的测试串
    bcrypt__ident="2b",
    bcrypt__truncate_error=False
)

@app.post("/auth/register", response_model=UserOut)
def register(user: UserIn, db: Session = Depends(get_db)):
    """
    1. 检查用户名重复
    2. 密码哈希
    3. 入库
    4. 返回不含密码的用户信息
    """
    # ① 唯一性检查
    if db.query(UserORM).filter(UserORM.username == user.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # ② 哈希密码（明文立刻丢弃）
   # 截断到 72 字节，避免 bcrypt 抛错

    plain_bytes = user.password.encode('utf-8')[:72]
    plain_str   = plain_bytes.decode('utf-8', errors='ignore')
    hash_       = pwd_ctx.hash(plain_str)

    # ③ 入库
    new_user = UserORM(username=user.username, password_hash=hash_)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # ④ 返回（不含密码）
    return UserOut(id=new_user.id, username=new_user.username) # type: ignore


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