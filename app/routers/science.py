from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from database import get_db
from app.models.science import Invitation, Abstract
from app.models.participants import Participant
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/science", tags=["science"])


class InvitationBase(BaseModel):
    participant_id: int
    status: str = "sent"


class InvitationCreate(InvitationBase):
    pass


class InvitationResponse(InvitationBase):
    id: int
    sent_at: datetime

    class Config:
        from_attributes = True


class AbstractBase(BaseModel):
    participant_id: int
    title: str
    content: str


class AbstractCreate(AbstractBase):
    pass


class AbstractResponse(AbstractBase):
    id: int
    status: str = "submitted"
    submitted_at: datetime = datetime.utcnow()

    class Config:
        from_attributes = True


@router.post("/invitations/", response_model=InvitationResponse)
def create_invitation(invitation: InvitationCreate, db: Session = Depends(get_db)):
    db_invitation = Invitation(**invitation.model_dump())
    db.add(db_invitation)
    db.commit()
    db.refresh(db_invitation)
    return db_invitation


@router.get("/invitations/", response_model=list[InvitationResponse])
def get_invitations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Invitation).offset(skip).limit(limit).all()


@router.delete("/invitations/{invitation_id}", status_code=204)
def delete_invitation(invitation_id: int, db: Session = Depends(get_db)):
    item = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Приглашение не найдено")
    db.delete(item)
    db.commit()
    return Response(status_code=204)


@router.post("/abstracts/", response_model=AbstractResponse)
def create_abstract(abstract: AbstractCreate, db: Session = Depends(get_db)):
    participant = (
        db.query(Participant).filter(Participant.id == abstract.participant_id).first()
    )
    if not participant:
        raise HTTPException(status_code=404, detail="Участник не найден")

    if participant.role != "speaker":
        raise HTTPException(
            status_code=400,
            detail="Подавать тезисы доклада могут только участники с ролью 'speaker'. При регистрации выберите правильную роль.",
        )

    db_abstract = Abstract(**abstract.model_dump())
    db.add(db_abstract)
    db.commit()
    db.refresh(db_abstract)
    return db_abstract


@router.get("/abstracts/", response_model=list[AbstractResponse])
def get_abstracts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Abstract).offset(skip).limit(limit).all()


@router.delete("/abstracts/{abstract_id}", status_code=204)
def delete_abstract(abstract_id: int, db: Session = Depends(get_db)):
    item = db.query(Abstract).filter(Abstract.id == abstract_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Тезисы не найдены")
    db.delete(item)
    db.commit()
    return Response(status_code=204)
