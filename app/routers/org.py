from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.models.org import Fee, Hotel, Mailing
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/org", tags=["organization"])


class FeeCreate(BaseModel):
    participant_id: int
    amount: float


class FeeResponse(FeeCreate):
    id: int
    status: str
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HotelCreate(BaseModel):
    participant_id: int
    check_in: str
    check_out: str


class HotelResponse(HotelCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class MailingCreate(BaseModel):
    participant_id: int
    subject: str
    body: str


class MailingResponse(MailingCreate):
    id: int
    status: str
    sent_at: datetime

    class Config:
        from_attributes = True


@router.post("/fees/", response_model=FeeResponse)
def create_fee(fee: FeeCreate, db: Session = Depends(get_db)):
    db_fee = Fee(**fee.model_dump())
    db.add(db_fee)
    db.commit()
    db.refresh(db_fee)
    return db_fee


@router.patch("/fees/{fee_id}/pay", response_model=FeeResponse)
def pay_fee(fee_id: int, db: Session = Depends(get_db)):
    fee = db.query(Fee).filter(Fee.id == fee_id).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Оргвзнос не найден")
    fee.status = "paid"
    fee.paid_at = datetime.utcnow()
    db.commit()
    db.refresh(fee)
    return fee


@router.post("/hotels/", response_model=HotelResponse)
def create_hotel(hotel: HotelCreate, db: Session = Depends(get_db)):
    """Заявка на бронирование гостиницы."""
    db_hotel = Hotel(**hotel.model_dump())
    db.add(db_hotel)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel


@router.patch("/hotels/{hotel_id}/book", response_model=HotelResponse)
def book_hotel(hotel_id: int, db: Session = Depends(get_db)):

    # Бронирование гостиницы.
    # БИЗНЕС-ПРАВИЛО: только при оплаченном оргвзносе!
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Заявка на гостиницу не найдена")

    # Проверяем, оплатил ли участник взнос
    fee = (
        db.query(Fee)
        .filter(Fee.participant_id == hotel.participant_id, Fee.status == "paid")
        .first()
    )

    if not fee:
        raise HTTPException(
            status_code=400,
            detail="Невозможно забронировать гостиницу: оргвзнос не оплачен",
        )

    hotel.status = "booked"
    db.commit()
    db.refresh(hotel)
    return hotel


@router.post("/mailings/", response_model=MailingResponse)
def create_mailing(mailing: MailingCreate, db: Session = Depends(get_db)):
    db_mailing = Mailing(**mailing.model_dump())
    db.add(db_mailing)
    db.commit()
    db.refresh(db_mailing)
    return db_mailing


@router.get("/mailings/", response_model=list[MailingResponse])
def get_mailings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Mailing).offset(skip).limit(limit).all()
