"""
Модели данных для GBR Security System
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class UnitStatus(enum.Enum):
    """Статусы экипажа ГБР"""
    FREE = "free"
    BUSY = "busy"
    ARRIVED = "arrived"


class CallStatus(enum.Enum):
    """Статусы вызова"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Unit(Base):
    """Модель экипажа ГБР"""
    __tablename__ = "units"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    telegram_id = Column(String(20), unique=True, nullable=True, index=True)
    status = Column(Enum(UnitStatus), default=UnitStatus.FREE, nullable=False)
    phone = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связь с вызовами
    calls = relationship("Call", back_populates="unit")
    
    def __repr__(self):
        return f"<Unit(id={self.id}, name='{self.name}', status='{self.status.value}')>"


class Call(Base):
    """Модель вызова"""
    __tablename__ = "calls"
    
    id = Column(Integer, primary_key=True, index=True)
    object_name = Column(String(200), nullable=False)
    address = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    
    # Статус и привязка
    status = Column(Enum(CallStatus), default=CallStatus.PENDING, nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    assigned_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Связь с экипажем
    unit = relationship("Unit", back_populates="calls")
    
    def __repr__(self):
        return f"<Call(id={self.id}, object='{self.object_name}', status='{self.status.value}')>"