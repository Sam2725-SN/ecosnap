from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class StatusEnum(str, enum.Enum):
    pending     = "pending"
    in_progress = "in_progress"
    resolved    = "resolved"


class Complaint(Base):
    __tablename__ = "complaints"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    location    = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    image_url   = Column(String(500), nullable=True)
    status      = Column(Enum(StatusEnum), default=StatusEnum.pending)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reporter = relationship("User", back_populates="complaints")