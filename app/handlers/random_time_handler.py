import random
import asyncio
from datetime import datetime, timedelta
from app.handlers.base_handler import BaseHandler
from app.config.settings import settings
from app.scheduler.scheduler import logger
from app.telegram.post import post_random_photo

class RandomTimeHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.base_time = settings.RANDOM_TIME_BASE
        self.duration_minutes = settings.RANDOM_TIME_DURATION
        self.task = None  # Для хранения асинхронной задачи
        
    async def execute_task(self, delay_seconds: int):
        """Выполнение задачи после задержки"""
        await asyncio.sleep(delay_seconds)
        try:
            logger.info("Начало публикации фото в Telegram в случайное время")
            
            # Публикуем случайное фото
            result = await post_random_photo()
            
            if result:
                logger.info(f"Фото успешно опубликовано: {result}")
            else:
                logger.warning("Не удалось опубликовать фото")
                
        except Exception as e:
            logger.error(f"Ошибка при публикации фото: {str(e)}")
    
        
    def handle(self):
        try:
            now = datetime.now()
            # Добавляем случайное количество минут к текущему времени
            random_minutes = random.randint(0, self.duration_minutes)
            random_time = now + timedelta(minutes=random_minutes)
            
            # Вычисляем задержку в секундах
            delay_seconds = (random_time - now).total_seconds()
            
            logger.info(f"Запланирована публикация фото на {random_time.strftime('%H:%M')} (через {delay_seconds:.0f} секунд)")
            
            # Создаем и запускаем новый event loop для асинхронной задачи
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Отменяем предыдущую задачу, если она есть
            if self.task and not self.task.done():
                self.task.cancel()
            
            # Создаем новую асинхронную задачу
            self.task = loop.create_task(self.execute_task(delay_seconds))
            
            # Запускаем задачу в отдельном потоке
            def run_task():
                loop.run_until_complete(self.task)
                loop.close()
            
            import threading
            thread = threading.Thread(target=run_task)
            thread.daemon = True
            thread.start()
            
            return {
                'status': 'success',
                'scheduled_time': random_time.strftime('%H:%M'),
                'delay_seconds': delay_seconds
            }
            
        except Exception as e:
            logger.error(f"Ошибка при планировании случайного времени: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
            
    def get_schedule_time(self):
        """Получить базовое время запуска"""
        return self.base_time 