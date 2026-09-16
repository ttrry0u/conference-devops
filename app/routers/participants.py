from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from database import get_db
from app.models.participants import Participant
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/participants", tags=["participants"])


class ParticipantBase(BaseModel):
    full_name: str
    email: EmailStr
    role: str = "attendee"
    is_online: bool = False


class ParticipantCreate(ParticipantBase):
    pass


class ParticipantResponse(ParticipantBase):
    id: int

    class Config:
        from_attributes = True


@router.post("/", response_model=ParticipantResponse)
def create_participant(participant: ParticipantCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(Participant).filter(Participant.email == participant.email).first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Участник с таким email уже существует"
        )

    db_participant = Participant(**participant.model_dump())
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant


@router.get("/", response_model=list[ParticipantResponse])
def get_participants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Participant).offset(skip).limit(limit).all()


@router.get("/{participant_id}", response_model=ParticipantResponse)
def get_participant(participant_id: int, db: Session = Depends(get_db)):
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Участник не найден")
    return participant


@router.delete("/{participant_id}", status_code=204)
def delete_participant(participant_id: int, db: Session = Depends(get_db)):
    item = db.query(Participant).filter(Participant.id == participant_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Участник не найден")
    db.delete(item)
    db.commit()
    return Response(status_code=204)
