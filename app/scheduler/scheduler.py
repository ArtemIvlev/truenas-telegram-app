import logging
import time
from datetime import datetime
from typing import Dict, List, Callable
import schedule

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        self.jobs: Dict[str, Dict] = {}
        self.handlers: Dict[str, Callable] = {}
        
    def add_job(self, job_id: str, handler: Callable, schedule_time: str, **kwargs):
        """
        Добавить задачу в расписание
        
        Args:
            job_id: Уникальный идентификатор задачи
            handler: Функция-обработчик
            schedule_time: Время выполнения в формате cron или human-readable
            **kwargs: Дополнительные параметры для задачи
        """
        self.handlers[job_id] = handler
        self.jobs[job_id] = {
            'schedule': schedule_time,
            'kwargs': kwargs,
            'last_run': None
        }
        
        # Добавляем задачу в schedule
        if schedule_time.startswith('every'):
            # Для human-readable формата (every 5 minutes, every day at 10:30 и т.д.)
            getattr(schedule.every(), schedule_time.split()[1])(handler).tag(job_id)
        else:
            # Для cron-подобного формата
            schedule.every().day.at(schedule_time).do(handler).tag(job_id)
            
        logger.info(f"Добавлена задача {job_id} с расписанием {schedule_time}")
        
    def remove_job(self, job_id: str):
        """Удалить задачу из расписания"""
        if job_id in self.jobs:
            schedule.clear(job_id)
            del self.jobs[job_id]
            del self.handlers[job_id]
            logger.info(f"Задача {job_id} удалена")
            
    def get_job_status(self, job_id: str) -> Dict:
        """Получить статус задачи"""
        if job_id in self.jobs:
            return {
                'id': job_id,
                'schedule': self.jobs[job_id]['schedule'],
                'last_run': self.jobs[job_id]['last_run'],
                'next_run': self._get_next_run(job_id)
            }
        return {}
        
    def _get_next_run(self, job_id: str) -> datetime:
        """Получить время следующего запуска задачи"""
        job = schedule.get_jobs(job_id)[0]
        return job.next_run
        
    def run_pending(self):
        """Запустить все ожидающие задачи"""
        schedule.run_pending()
        
    def run_forever(self, interval: int = 1):
        """
        Запустить шедулер в бесконечном цикле
        
        Args:
            interval: Интервал проверки в секундах
        """
        logger.info("Запуск шедулера...")
        while True:
            try:
                self.run_pending()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Ошибка в шедулере: {e}")
                time.sleep(60)  # В случае ошибки ждем минуту 