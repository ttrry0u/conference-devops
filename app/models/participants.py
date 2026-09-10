from sqlalchemy import Column, Integer, String, Boolean
from database import Base


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default="attendee")
    is_online = Column(Boolean, default=False)
