from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy import Column
from long_stream.db.database import get_db_session
from long_stream.models.sentence import SentenceIn, SentenceORM, SentenceOut
from sqlalchemy.orm import Session

sentence_router = APIRouter(prefix="/sentences", tags=["句子管理"])


@sentence_router.post("/add", response_model=SentenceOut)
def create_sentence(sentence: SentenceIn, db: Session = Depends(get_db_session)):
    new_sentence = SentenceORM(content=sentence.content, author=sentence.author)
    db.add(new_sentence)
    db.commit()
    db.refresh(new_sentence)
    return SentenceOut(**new_sentence.__dict__)


@sentence_router.post("/read/{sentence_id}", response_model=SentenceOut)
def read_sentence(sentence_id: int, db: Session = Depends(get_db_session)):
    sentence = db.get(SentenceORM, sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="句子不存在")
    return SentenceOut(**sentence.__dict__)


@sentence_router.post("/query", response_model=list[SentenceOut])
def list_sentences(db: Session = Depends(get_db_session)):
    sentences = db.query(SentenceORM).all()
    return [SentenceOut(**sentence.__dict__) for sentence in sentences]


@sentence_router.post("/update/{sentence_id}", response_model=SentenceOut)
def update_sentence(
    sentence_id: int, req_sentence: SentenceIn, db: Session = Depends(get_db_session)
):
    sentence = db.get(SentenceORM, sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="句子不存在")
    sentence.content = Column(req_sentence.content)
    sentence.author = Column(req_sentence.author)
    db.commit()
    db.refresh(sentence)
    return SentenceOut(**sentence.__dict__)


@sentence_router.post("/delete/{sentence_id}")
def delete_sentence(sentence_id: int, db: Session = Depends(get_db_session)):
    sentence = db.get(SentenceORM, sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="句子不存在")
    db.delete(sentence)
    db.commit()
