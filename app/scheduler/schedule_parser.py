import re
from datetime import datetime
from typing import Dict, Union, Tuple
from croniter import croniter

class ScheduleParser:
    """Парсер для разбора cron-расписания"""
    
    @staticmethod
    def parse(schedule_str: str) -> Dict[str, Union[str, int, str]]:
        """
        Разбирает строку расписания в cron-формате
        
        Args:
            schedule_str: Строка расписания в cron-формате:
                * * * * *
                │ │ │ │ │
                │ │ │ │ └─ день недели (0-6) (воскресенье=0)
                │ │ │ └─── месяц (1-12)
                │ │ └───── день месяца (1-31)
                │ └─────── час (0-23)
                └───────── минута (0-59)
                
        Returns:
            Dict с параметрами расписания:
                - type: "cron"
                - value: исходная cron-строка
                
        Raises:
            ValueError: если формат расписания неверный
        """
        try:
            # Проверяем валидность cron-выражения
            croniter(schedule_str, datetime.now())
            return {
                'type': 'cron',
                'value': schedule_str
            }
        except Exception as e:
            raise ValueError(f"Неверный формат cron-расписания: {str(e)}")
        
    @staticmethod
    def validate(schedule_str: str) -> bool:
        """
        Проверяет корректность cron-строки
        
        Args:
            schedule_str: Строка расписания для проверки
            
        Returns:
            bool: True если формат корректный
        """
        try:
            ScheduleParser.parse(schedule_str)
            return True
        except ValueError:
            return False
            
    @staticmethod
    def get_next_run(schedule_str: str, from_time: datetime = None) -> datetime:
        """
        Вычисляет время следующего запуска по cron-расписанию
        
        Args:
            schedule_str: Строка cron-расписания
            from_time: Время, от которого считать следующий запуск
                      (по умолчанию текущее время)
                      
        Returns:
            datetime: Время следующего запуска
        """
        if from_time is None:
            from_time = datetime.now()
            
        cron = croniter(schedule_str, from_time)
        return cron.get_next(datetime) 