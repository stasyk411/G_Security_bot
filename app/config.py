"""
Конфигурация системы GBR Security
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()


class Config:
    """Класс конфигурации приложения"""
    
    def __init__(self):
        self.dispatcher_bot_token: str = self._get_required_env("DISPATCHER_BOT_TOKEN")
        self.crew_bot_token: str = self._get_required_env("CREW_BOT_TOKEN")
        self.dispatcher_id: int = self._get_required_int_env("DISPATCHER_ID")
        self.database_url: str = self._get_env("DATABASE_URL", "sqlite:///gbr_security.db")
        
    @staticmethod
    def _get_required_env(key: str) -> str:
        """Получение обязательной переменной окружения"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Переменная окружения {key} обязательна")
        return value
    
    @staticmethod
    def _get_required_int_env(key: str) -> int:
        """Получение обязательной числовой переменной окружения"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Переменная окружения {key} обязательна")
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Переменная окружения {key} должна быть числом")
    
    @staticmethod
    def _get_env(key: str, default: Optional[str] = None) -> str:
        """Получение переменной окружения с значением по умолчанию"""
        return os.getenv(key, default or "")


# Глобальный экземпляр конфигурации
config = Config()
