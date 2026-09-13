from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from database import Base
from datetime import datetime


class Fee(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="unpaid")
    paid_at = Column(DateTime, nullable=True)


class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    check_in = Column(String, nullable=False)
    check_out = Column(String, nullable=False)
    status = Column(String, default="requested")
    created_at = Column(DateTime, default=datetime.utcnow)


class Mailing(Base):
    __tablename__ = "mailings"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)
    status = Column(String, default="sent")
    sent_at = Column(DateTime, default=datetime.utcnow)
