import os
import logging
from dotenv import load_dotenv
from app.scheduler.scheduler import Scheduler
from app.handlers.file_check_handler import FileCheckHandler
from app.handlers.detect_nude_handler import DetectNudeHandler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

def main():
    try:
        scheduler = Scheduler()
        
        # Добавляем задачу проверки файлов
        scheduler.add_job(
            job_id='check_files',
            handler=FileCheckHandler().handle,
            schedule_time='every 5 minutes'
        )
        
        # Добавляем задачу detect_nude.py
        scheduler.add_job(
            job_id='detect_nude',
            handler=DetectNudeHandler().handle,
            schedule_time='every 1 days'
        )
        
        # Запускаем планировщик
        scheduler.run()
        
    except Exception as e:
        logger.error(f"Ошибка в главном процессе: {str(e)}")
        raise

if __name__ == "__main__":
    main() 