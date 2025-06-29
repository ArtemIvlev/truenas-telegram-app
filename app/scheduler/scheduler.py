import logging
import time
from datetime import datetime
from typing import Dict, List, Callable
import schedule
from croniter import croniter

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        self.jobs: Dict[str, Dict] = {}
        self.handlers: Dict[str, Callable] = {}
        
    def add_job(self, job_id: str, handler: Callable, schedule_time: str, run_now: bool = False):
        """Add a new job to the scheduler
        
        Args:
            job_id (str): Unique identifier for the job
            handler (Callable): Function to execute
            schedule_time (str): Schedule time in cron format or 'HH:MM'
            run_now (bool): Whether to run the job immediately
        """
        if ':' in schedule_time:  # Формат времени HH:MM
            schedule.every().day.at(schedule_time).do(handler).tag(job_id)
        elif schedule_time.startswith('every'):
            time_parts = schedule_time.split()
            if len(time_parts) != 3:
                raise ValueError("Invalid schedule time format. Use 'every X minutes/hours/days' or 'HH:MM'")
                
            interval = int(time_parts[1])
            unit = time_parts[2]
            
            if unit == 'minutes':
                schedule.every(interval).minutes.do(handler).tag(job_id)
            elif unit == 'hours':
                schedule.every(interval).hours.do(handler).tag(job_id)
            elif unit == 'days':
                schedule.every(interval).days.do(handler).tag(job_id)
            else:
                raise ValueError("Invalid time unit. Use minutes, hours, or days")
        else:  # Cron format
            try:
                # Проверяем валидность cron выражения
                croniter(schedule_time, datetime.now())
                # Преобразуем cron в формат schedule
                minute, hour, day, month, weekday = schedule_time.split()
                if minute != '*':
                    # Форматируем время в формат HH:MM
                    time_str = f"{int(hour):02d}:{int(minute):02d}"
                    schedule.every().day.at(time_str).do(handler).tag(job_id)
                else:
                    time_str = f"{int(hour):02d}:00"
                    schedule.every().day.at(time_str).do(handler).tag(job_id)
            except Exception as e:
                raise ValueError(f"Invalid cron format: {str(e)}")
            
        self.handlers[job_id] = handler
        self.jobs[job_id] = {
            'handler': handler,
            'schedule_time': schedule_time,
            'last_run': None
        }
        
        logger.info(f"Добавлена задача {job_id} с расписанием {schedule_time}")
        
        # Запускаем задачу немедленно, если указано
        if run_now:
            logger.info(f"Немедленный запуск задачи {job_id}")
            handler()
            
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
                'schedule': self.jobs[job_id]['schedule_time'],
                'last_run': self.jobs[job_id]['last_run'],
                'next_run': self._get_next_run(job_id)
            }
        return {}
        
    def _get_next_run(self, job_id: str) -> datetime:
        """Получить время следующего запуска задачи"""
        job = schedule.get_jobs(job_id)[0]
        return job.next_run
        
    def run(self):
        """Run the scheduler"""
        logger.info("Запуск шедулера...")
        while True:
            schedule.run_pending()
            time.sleep(1)
        
    def run_forever(self, interval: int = 1):
        """
        Запустить шедулер в бесконечном цикле
        
        Args:
            interval: Интервал проверки в секундах
        """
        logger.info("Запуск шедулера...")
        while True:
            try:
                schedule.run_pending()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Ошибка в шедулере: {e}")
                time.sleep(60)  # В случае ошибки ждем минуту 