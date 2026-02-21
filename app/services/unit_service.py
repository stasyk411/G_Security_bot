"""
Сервис для работы с экипажами ГБР
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database import SessionLocal
from app.models import Unit, UnitStatus


def create_unit(
    name: str,
    telegram_id: Optional[str] = None,
    phone: Optional[str] = None,
    notes: Optional[str] = None,
) -> Unit:
    session: Session = SessionLocal()
    try:
        unit = Unit(
            name=name,
            telegram_id=telegram_id,
            phone=phone,
            notes=notes,
            status=UnitStatus.FREE,
        )
        session.add(unit)
        session.commit()
        session.refresh(unit)
        return unit
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def get_free_units() -> List[Unit]:
    session: Session = SessionLocal()
    try:
        return session.query(Unit).filter(Unit.status == UnitStatus.FREE).all()
    finally:
        session.close()


def set_unit_status(unit_id: int, status: str) -> Optional[Unit]:
    session: Session = SessionLocal()
    try:
        unit = session.query(Unit).filter(Unit.id == unit_id).first()
        if not unit:
            return None

        status_mapping = {
            "free": UnitStatus.FREE,
            "busy": UnitStatus.BUSY,
            "arrived": UnitStatus.ARRIVED,
        }

        if status not in status_mapping:
            raise ValueError(f"Неверный статус: {status}")

        unit.status = status_mapping[status]
        session.commit()
        session.refresh(unit)
        return unit
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def get_unit_by_id(unit_id: int) -> Optional[Unit]:
    session: Session = SessionLocal()
    try:
        return session.query(Unit).filter(Unit.id == unit_id).first()
    finally:
        session.close()


def get_unit_by_telegram_id(telegram_id: str) -> Optional[Unit]:
    session: Session = SessionLocal()
    try:
        return session.query(Unit).filter(Unit.telegram_id == telegram_id).first()
    finally:
        session.close()


def get_all_units() -> List[Unit]:
    session: Session = SessionLocal()
    try:
        return session.query(Unit).all()
    finally:
        session.close()