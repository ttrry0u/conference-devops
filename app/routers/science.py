from fastapi import APIRouter, Depends #HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.models.science import Invitation, Abstract
from pydantic import BaseModel
from datetime import datetime
#from typing import Optional

router = APIRouter(prefix="/science", tags=["science"])


# cхемы для Приглашений
class InvitationBase(BaseModel):
    participant_id: int
    status: str = "sent"


# cхема для создания
class InvitationCreate(InvitationBase):
    pass


# cхема для ответа
class InvitationResponse(InvitationBase):
    id: int
    sent_at: datetime

    class Config:
        from_attributes = True


# cхемы для Тезисов
class AbstractBase(BaseModel):
    participant_id: int
    title: str
    content: str


class AbstractCreate(AbstractBase):
    pass


class AbstractResponse(AbstractBase):
    id: int
    status: str
    submitted_at: datetime

    class Config:
        from_attributes = True


# операции с приглашениями


# POST-запрос для создания нового приглашения
@router.post("/invitations/", response_model=InvitationResponse)
def create_invitation(invitation: InvitationCreate, db: Session = Depends(get_db)):
    db_invitation = Invitation(**invitation.model_dump())

    db.add(db_invitation)
    db.commit()
    db.refresh(db_invitation)
    return db_invitation


# GET-запрос для получения списка всех приглашений
@router.get("/invitations/", response_model=list[InvitationResponse])
def get_invitations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Делаем выборку из БД с поддержкой пагинации (skip и limit)
    return db.query(Invitation).offset(skip).limit(limit).all()


# POST-запрос для подачи тезисов
@router.post("/abstracts/", response_model=AbstractResponse)
def create_abstract(abstract: AbstractCreate, db: Session = Depends(get_db)):
    db_abstract = Abstract(**abstract.model_dump())
    db.add(db_abstract)
    db.commit()
    db.refresh(db_abstract)
    return db_abstract


# GET-запрос для получения списка всех тезисов
@router.get("/abstracts/", response_model=list[AbstractResponse])
def get_abstracts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Abstract).offset(skip).limit(limit).all()
