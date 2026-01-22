from fastapi import APIRouter, Request
from fastapi import Depends, HTTPException
from sqlalchemy import Column
from db.database import get_db_session
from models import get_db
from models.orm import SentenceORM, UserORM
from models.sentence import SentenceIn, SentenceOut
from sqlalchemy.orm import Session
from utils.auth import get_optional_user, require_admin, require_user, verify_token
from models.token import TokenData

sentence_router = APIRouter(prefix="/sentences", tags=["句子管理"])


@sentence_router.post("/add", response_model=SentenceOut)
def create_sentence(sentence: SentenceIn, db: Session = Depends(get_db_session), current_user = Depends(require_user)):
    new_sentence = SentenceORM(content=sentence.content, author=sentence.author)
    db.add(new_sentence)
    db.commit()
    db.refresh(new_sentence)
    return SentenceOut(**new_sentence.__dict__)


@sentence_router.post("/read/{sentence_id}", response_model=SentenceOut)
def read_sentence(sentence_id: int, db: Session = Depends(get_db_session), current_user = Depends(get_optional_user)):
    sentence = db.get(SentenceORM, sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="句子不存在")
    return SentenceOut(**sentence.__dict__)


@sentence_router.post("/query", response_model=list[SentenceOut])
def list_sentences(db: Session = Depends(get_db_session), current_user = Depends(get_optional_user)):
    sentences = db.query(SentenceORM).all()
    return [SentenceOut(**sentence.__dict__) for sentence in sentences]


@sentence_router.post("/update/{sentence_id}", response_model=SentenceOut)
def update_sentence(
    sentence_id: int,
    sentence_data: dict,
    db: Session = Depends(get_db_session),
    current_user = Depends(require_user)
):
    sentence = db.get(SentenceORM, sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="句子不存在")
    # 安全地更新已有字段
    for key, value in sentence_data.items():
        if hasattr(sentence, key):
            setattr(sentence, key, value)
    db.commit()
    db.refresh(sentence)
    return SentenceOut(**sentence.__dict__)


@sentence_router.post("/delete/{sentence_id}")
def delete_sentence(
    sentence_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_user)
):
    sentence = db.query(SentenceORM).filter(SentenceORM.id == sentence_id).first()
    if not sentence:
        raise HTTPException(status_code=404)
    if sentence.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403)
    db.delete(sentence)
    db.commit()
    return {"ok": True}

@sentence_router.post("/users/{user_id}", dependencies=[Depends(require_admin)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return {"ok": True}