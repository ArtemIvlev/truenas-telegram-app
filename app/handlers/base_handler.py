import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

logger = logging.getLogger(__name__)

class BaseHandler(ABC):
    def __init__(self, **kwargs):
        self.config = kwargs
        
    @abstractmethod
    def handle(self) -> Dict[str, Any]:
        """
        Обработка задачи
        
        Returns:
            Dict с результатами выполнения
        """
        pass
        
    def validate(self) -> bool:
        """
        Валидация конфигурации обработчика
        
        Returns:
            bool: True если конфигурация валидна
        """
        return True
        
    def before_run(self):
        """Действия перед выполнением задачи"""
        logger.info(f"Начало выполнения задачи {self.__class__.__name__}")
        
    def after_run(self, result: Dict[str, Any]):
        """Действия после выполнения задачи"""
        logger.info(f"Задача {self.__class__.__name__} выполнена с результатом: {result}")
        
    def on_error(self, error: Exception):
        """Обработка ошибок"""
        logger.error(f"Ошибка в задаче {self.__class__.__name__}: {error}") 