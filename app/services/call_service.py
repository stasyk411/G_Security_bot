"""
Сервис для работы с вызовами
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from datetime import datetime
from app.database import SessionLocal
from app.models import Call, CallStatus, Unit


class CallService:
    """Сервис для управления вызовами"""
    
    @staticmethod
    def create_call(object_name: str, address: str, description: Optional[str] = None, 
                   latitude: Optional[str] = None, longitude: Optional[str] = None) -> Call:
        """
        Создание нового вызова
        
        Args:
            object_name: Название объекта
            address: Адрес объекта
            description: Описание вызова
            latitude: Широта
            longitude: Долгота
            
        Returns:
            Call: Созданный вызов
            
        Raises:
            SQLAlchemyError: Ошибка базы данных
        """
        session: Session = SessionLocal()
        try:
            call = Call(
                object_name=object_name,
                address=address,
                description=description,
                latitude=latitude,
                longitude=longitude,
                status=CallStatus.PENDING
            )
            session.add(call)
            session.commit()
            session.refresh(call)
            return call
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def assign_call_to_unit(call_id: int, unit_id: int) -> Optional[Call]:
        """
        Назначение вызова на экипаж
        
        Args:
            call_id: ID вызова
            unit_id: ID экипажа
            
        Returns:
            Optional[Call]: Обновленный вызов или None если не найден
        """
        session: Session = SessionLocal()
        try:
            call = session.query(Call).filter(Call.id == call_id).first()
            if not call:
                return None
            
            unit = session.query(Unit).filter(Unit.id == unit_id).first()
            if not unit:
                return None
            
            # Назначаем вызов на экипаж
            call.unit_id = unit_id
            call.status = CallStatus.ASSIGNED
            call.assigned_at = datetime.utcnow()
            
            # Обновляем статус экипажа на занят
            from app.services.unit_service import UnitService
            UnitService.set_unit_status(unit_id, 'busy')
            
            session.commit()
            session.refresh(call)
            return call
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def set_call_status(call_id: int, status: str) -> Optional[Call]:
        """
        Установка статуса вызова
        
        Args:
            call_id: ID вызова
            status: Новый статус ('pending', 'assigned', 'in_progress', 'completed')
            
        Returns:
            Optional[Call]: Обновленный вызов или None если не найден
        """
        session: Session = SessionLocal()
        try:
            call = session.query(Call).filter(Call.id == call_id).first()
            if not call:
                return None
            
            # Преобразование строкового статуса в enum
            status_mapping = {
                'pending': CallStatus.PENDING,
                'assigned': CallStatus.ASSIGNED,
                'in_progress': CallStatus.IN_PROGRESS,
                'completed': CallStatus.COMPLETED
            }
            
            if status not in status_mapping:
                raise ValueError(f"Неверный статус: {status}")
            
            call.status = status_mapping[status]
            
            # Устанавливаем временные метки
            if status == 'completed':
                call.completed_at = datetime.utcnow()
                # Освобождаем экипаж
                if call.unit_id:
                    from app.services.unit_service import UnitService
                    UnitService.set_unit_status(call.unit_id, 'free')
            elif status == 'in_progress':
                # Меняем статус экипажа на прибыл
                if call.unit_id:
                    from app.services.unit_service import UnitService
                    UnitService.set_unit_status(call.unit_id, 'arrived')
            
            session.commit()
            session.refresh(call)
            return call
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_call_by_id(call_id: int) -> Optional[Call]:
        """
        Получение вызова по ID
        
        Args:
            call_id: ID вызова
            
        Returns:
            Optional[Call]: Вызов или None если не найден
        """
        session: Session = SessionLocal()
        try:
            call = session.query(Call).filter(Call.id == call_id).first()
            return call
        finally:
            session.close()
    
    @staticmethod
    def get_pending_calls() -> List[Call]:
        """
        Получение ожидающих вызовов
        
        Returns:
            List[Call]: Список ожидающих вызовов
        """
        session: Session = SessionLocal()
        try:
            calls = session.query(Call).filter(Call.status == CallStatus.PENDING).all()
            return calls
        finally:
            session.close()
    
    @staticmethod
    def get_active_calls() -> List[Call]:
        """
        Получение активных вызовов (assigned и in_progress)
        
        Returns:
            List[Call]: Список активных вызовов
        """
        session: Session = SessionLocal()
        try:
            calls = session.query(Call).filter(
                Call.status.in_([CallStatus.ASSIGNED, CallStatus.IN_PROGRESS])
            ).all()
            return calls
        finally:
            session.close()
    
    @staticmethod
    def get_calls_by_unit(unit_id: int) -> List[Call]:
        """
        Получение вызовов экипажа
        
        Args:
            unit_id: ID экипажа
            
        Returns:
            List[Call]: Список вызовов экипажа
        """
        session: Session = SessionLocal()
        try:
            calls = session.query(Call).filter(Call.unit_id == unit_id).all()
            return calls
        finally:
            session.close()
    
    @staticmethod
    def get_all_calls() -> List[Call]:
        """
        Получение всех вызовов
        
        Returns:
            List[Call]: Список всех вызовов
        """
        session: Session = SessionLocal()
        try:
            calls = session.query(Call).all()
            return calls
        finally:
            session.close()
