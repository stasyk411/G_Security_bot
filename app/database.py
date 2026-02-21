"""
Настройки базы данных для GBR Security System
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import config

# Создание движка базы данных
engine = create_engine(
    config.database_url,
    echo=False,  # Установить True для отладки SQL запросов
    pool_pre_ping=True,  # Проверка соединения перед использованием
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Декларативная база для моделей
Base = declarative_base()


def get_db():
    """
    Получение сессии базы данных
    Используется как dependency injection
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Инициализация базы данных
    Создание всех таблиц
    """
    from app.models import Unit, Call  # Импорт моделей для регистрации
    Base.metadata.create_all(bind=engine)
    print("База данных успешно инициализирована")
