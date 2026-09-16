from fastapi import APIRouter, Depends, HTTPException, Response
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
    """Заявка на бронирование гостиницы с валидацией дат."""
    from datetime import date, datetime as dt

    try:
        check_in_date = dt.strptime(hotel.check_in, "%Y-%m-%d").date()
        check_out_date = dt.strptime(hotel.check_out, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Неверный формат даты. Используйте ГГГГ-ММ-ДД"
        )

    if check_in_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Дата заезда не может быть в прошлом. Укажите будущую дату.",
        )

    if check_out_date <= check_in_date:
        raise HTTPException(
            status_code=400, detail="Дата выезда должна быть СТРОГО позже даты заезда!"
        )

    db_hotel = Hotel(**hotel.model_dump())
    db.add(db_hotel)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel


@router.patch("/hotels/{hotel_id}/book", response_model=HotelResponse)
def book_hotel(hotel_id: int, db: Session = Depends(get_db)):

    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Заявка на гостиницу не найдена")

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


@router.delete("/fees/{fee_id}", status_code=204)
def delete_fee(fee_id: int, db: Session = Depends(get_db)):
    item = db.query(Fee).filter(Fee.id == fee_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Взнос не найден")
    db.delete(item)
    db.commit()
    return Response(status_code=204)


@router.delete("/hotels/{hotel_id}", status_code=204)
def delete_hotel(hotel_id: int, db: Session = Depends(get_db)):
    item = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    db.delete(item)
    db.commit()
    return Response(status_code=204)


@router.delete("/mailings/{mailing_id}", status_code=204)
def delete_mailing(mailing_id: int, db: Session = Depends(get_db)):
    item = db.query(Mailing).filter(Mailing.id == mailing_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Рассылка не найдена")
    db.delete(item)
    db.commit()
    return Response(status_code=204)


@router.get("/fees/", response_model=list[FeeResponse])
def get_fees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Fee).offset(skip).limit(limit).all()


@router.get("/hotels/", response_model=list[HotelResponse])
def get_hotels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Hotel).offset(skip).limit(limit).all()
