from sqlalchemy import Column, \
    Integer, \
    String, \
    ForeignKey, \
    DateTime
from database import Base
from datetime import datetime

#приглашения
class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True) #первичный ключ
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False) #внешний ключ
    status = Column(String, default="sent")
    sent_at = Column(DateTime, default=datetime.utcnow)

#тезисы
class Abstract(Base):
    __tablename__ = "abstracts"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    status = Column(String, default="pending")
    submitted_at = Column(DateTime, default=datetime.utcnow)